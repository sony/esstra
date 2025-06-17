/*
 * SPDX-FileCopyrightText: Copyright 2024-2025 Sony Group Corporation
 * SPDX-License-Identifier: GPL-3.0-or-later
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

#include <stdio.h>
#include <limits.h>
#include <errno.h>
#include <unistd.h>
#include <libgen.h>

#include <string>
#include <vector>
#include <map>
#include <set>
#include <algorithm>
#include <iostream>
#include <iomanip>

#include "gcc-plugin.h"
#include "output.h"
#include "plugin-version.h"

#include "WjCryptLib_Md5.h"
#include "WjCryptLib_Sha1.h"
#include "WjCryptLib_Sha256.h"


using std::vector;
using std::string;
using std::map;
using std::set;
using std::stringstream;
using std::string_literals::operator""s;

int plugin_is_GPL_compatible;


// version numbers
static constexpr char tool_name[] = "ESSTRA Core";
static constexpr char tool_version[] = "0.1.1-develop";
static constexpr char data_format_version[] = "0.1.0-develop";

// section name
static constexpr char section_name[] = ".esstra";

// metadata
static vector<string> allpaths;
using FileInfo = map<string, string>;
static std::map<string, FileInfo> infomap;

// hash algorithms
static const vector<string> supported_algos = {
    "md5",
    "sha1",
    "sha256",
};
static vector<string> specified_algos = { // embeds sha1 sum by default
    "sha1",
};

// yaml
#define YAML_ITEM "- "s
#define YAML_INDENT "  "s
#define YAML_SEPARATOR "---"s

// keys
#define KEY_HEADERS "Headers"s
#define KEY_TOOL_NAME "ToolName"s
#define KEY_TOOL_VERSION "ToolVersion"s
#define KEY_DATA_FORMAT_VERSION "DataFormatVersion"s
#define KEY_INPUT_FILENAME "InputFileName"s
#define KEY_SOURCE_FILES "SourceFiles"s
#define KEY_FILE "File"s
#define KEY_MD5 "MD5"s
#define KEY_SHA1 "SHA1"s
#define KEY_SHA256 "SHA256"s

// flags
static bool flag_debug = false;


/*
 * debug print
 */
static void
debug_log(const char* format, ...) {
    if (flag_debug) {
        va_list args;
        va_start(args, format);
        printf("[DEBUG] ");
        vprintf(format, args);
        va_end(args);
    }
}

/*
 * convert byte data to hex string
 */
static const string
bytes_to_string(uint8_t* bytes, unsigned size) {
    stringstream hexstream;
    hexstream << std::hex << std::setfill('0');
    while (size--) {
        hexstream << std::setw(2) << static_cast<int>(*bytes++);
    }
    return hexstream.str();
}

/*
 * check if specified algorithm is supported
 */
static bool
is_algo_supported(const string& algo) {
    return std::find(supported_algos.begin(), supported_algos.end(), algo) != supported_algos.end();
}

/*
 * calculate md5sum
 */
static const string
calc_md5(uint8_t *buffer, uint32_t size) {
    MD5_HASH hash;
    Md5Calculate(buffer, size, &hash);
    return bytes_to_string(hash.bytes, MD5_HASH_SIZE);
}

/*
 * calculate sha1sum
 */
static const string
calc_sha1(uint8_t *buffer, uint32_t size) {
    SHA1_HASH hash;
    Sha1Calculate(buffer, size, &hash);
    return bytes_to_string(hash.bytes, SHA1_HASH_SIZE);
}

/*
 * calculate sha256sum
 */
static const string
calc_sha256(uint8_t *buffer, uint32_t size) {
    SHA256_HASH hash;
    Sha256Calculate(buffer, size, &hash);
    return bytes_to_string(hash.bytes, SHA256_HASH_SIZE);
}


/*
 * PLUGIN_INCLUDE_FILE handler - collect paths of source files
 */
static void
collect_paths(void* gcc_data, void* /* user_data */) {
    string path(reinterpret_cast<const char*>(gcc_data));

    if (path[0] == '<') {
        debug_log("skip '%s': pseudo file name\n", path.c_str());
        return;
    }

    // get absolute path

    char resolved[PATH_MAX];
    if (!realpath(path.c_str(), resolved)) {
        perror((path + ": realpath() failed").c_str());
        return;
    }

    string resolved_path(resolved);
    if (find(allpaths.begin(), allpaths.end(), resolved_path) != allpaths.end()) {
        debug_log("skip '%s': already registered\n", resolved_path.c_str());
        return;
    }

    allpaths.push_back(resolved_path);

    // calc checksum

    int fd = open(resolved, O_RDONLY);
    if (fd == 0) {
        perror("open() failed");
        return;
    }

    struct stat filestat;
    if (fstat(fd, &filestat) < 0) {
        perror((path + ": fstat() failed").c_str());
        return;
    }
    ssize_t st_size = (ssize_t)filestat.st_size;

    uint8_t* buffer = new uint8_t[st_size];
    ssize_t size = read(fd, buffer, st_size);
    if (size != st_size) {
        fprintf(stderr, "size mismatch: st_size:%lu, read():%zd\n", st_size, size);
        return;
    }

    // calculate hashes with specified algorithms
    FileInfo finfo;

    for (const auto &algo: specified_algos) {
        debug_log("calculate '%s' hash\n", algo.c_str());
        if (algo == "md5") {
            finfo[KEY_MD5] = "'" + calc_md5(buffer, size) + "'";
        } else if (algo == "sha1") {
            finfo[KEY_SHA1] = "'" + calc_sha1(buffer, size) + "'";
        } else if (algo == "sha256") {
            finfo[KEY_SHA256] = "'" + calc_sha256(buffer, size) + "'";
        } else {
            fprintf(stderr, "unsupported hash algorithm '%s'\n", algo.c_str());
        }
    }

    infomap[resolved] = finfo;

    delete[] buffer;
}

/*
 * PLUGIN_FINISH_UNIT handler - create a new ELF section and store path data in it
 */
static void
create_section(void* /* gcc_data */, void* /* user_data */) {
    vector<string> strings_to_embed;

    // construct metadata in yaml format
    strings_to_embed.push_back(YAML_SEPARATOR);

    // headers
    strings_to_embed.push_back(KEY_HEADERS + ":");
    strings_to_embed.push_back(YAML_INDENT + KEY_TOOL_NAME + ": " + tool_name);
    strings_to_embed.push_back(YAML_INDENT + KEY_TOOL_VERSION + ": " + tool_version);
    strings_to_embed.push_back(YAML_INDENT + KEY_DATA_FORMAT_VERSION + ": " + data_format_version);
    strings_to_embed.push_back(YAML_INDENT + KEY_INPUT_FILENAME + ": " + main_input_filename);

    // source files
    if (allpaths.size() == 0) {
        strings_to_embed.push_back(KEY_SOURCE_FILES + ": {}");
    } else {
        strings_to_embed.push_back(KEY_SOURCE_FILES + ":");

        // sort directories using std::set
        set<string> sorted_dirs;
        map<string, vector<string>> dir_to_files;
        for (const auto& path : allpaths) {
            string directory = dirname(const_cast<char*>(string(path).c_str()));
            string filename = basename(const_cast<char*>(string(path).c_str()));
            sorted_dirs.insert(directory);
            dir_to_files[directory].push_back(filename);
        }

        // enumerate all directories and files
        for (const auto& directory : sorted_dirs) {
            strings_to_embed.push_back(YAML_INDENT + directory + ":");
            for (const auto& filename : dir_to_files[directory]) {
                debug_log("dir: %s\n", directory.c_str());
                strings_to_embed.push_back(YAML_INDENT + YAML_ITEM + KEY_FILE + ": " + filename);
                string path = directory + "/" + filename;
                for (const auto& elem : infomap[path]) {
                    strings_to_embed.push_back(
                        YAML_INDENT + YAML_INDENT + elem.first + ": " + elem.second);
                }
            }
        }
    }

    // calculate size of metadata
    int datasize = 0;
    for (const auto& item : strings_to_embed) {
        datasize += item.size() + 1;  // plus 1 for null-character temination
    }
    int padding = 0;
    if (datasize % 4) {
        padding = 4 - datasize % 4;   // padding for 4-byte alignment
    }
    debug_log("size=%d\n", datasize);
    debug_log("padding=%d\n", padding);

    // add assembly code
    fprintf(asm_out_file, "\t.pushsection %s\n", section_name);
    fprintf(asm_out_file, "\t.balign 4\n");
    for (const auto& item : strings_to_embed) {
        fprintf(asm_out_file, "\t.ascii \"%s\\n\"\n", item.c_str());
    }
    if (padding > 0) {
        fprintf(asm_out_file, "\t.dcb.b %d,0x0a\n", padding);
    }
    fprintf(asm_out_file, "\t.popsection\n");
}

/*
 * initialization
 */
int
plugin_init(struct plugin_name_args* plugin_info,
            struct plugin_gcc_version* version) {
    if (!plugin_default_version_check(version, &gcc_version)) {
        return 1;
    }

    bool error = false;

    const struct plugin_argument *argv = plugin_info->argv;
    int argc = plugin_info->argc;

    while (argc--) {
        if (strcmp(argv->key, "debug") == 0) {
            flag_debug = (atoi(argv->value) != 0);
            if (flag_debug) {
                debug_log("debug mode enabled\n");
            }
        } else if (strcmp(argv->key, "checksum") == 0) {
            debug_log("arg-checksum: %s\n", argv->value);
            auto value = reinterpret_cast<const char*>(argv->value);
            string algo;
            specified_algos.clear(); // delete default algo
            while (*value) {
                if (*value == ',') {
                    if (algo.length() > 0) {
                        specified_algos.push_back(algo);
                    }
                    algo = "";
                } else {
                    algo += string(value, 1);
                }
                value++;
            }
            if (algo.length() > 0) {
                specified_algos.push_back(algo);
            }
            // check if specified algos are supported
            for (const auto& algo: specified_algos) {
                if (!is_algo_supported(algo)) {
                    fprintf(stderr, "algorithm '%s' not supported\n", algo.c_str());
                    error = true;
                }
                debug_log("algo: '%s'\n", algo.c_str());
            }
        }
        argv++;
    }

    debug_log("main_input_filename: %s\n", main_input_filename);

    if (error) {
        fprintf(stderr, "error occurred.");
        return 1;
    }

    register_callback(plugin_info->base_name,
                      PLUGIN_INCLUDE_FILE, collect_paths, 0);

    register_callback(plugin_info->base_name,
                      PLUGIN_FINISH_UNIT, create_section, 0);

    return 0;
}
