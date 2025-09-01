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

int plugin_is_GPL_compatible;


// version numbers
static const string tool_name = "ESSTRA Core";
static const string tool_version = "0.3.0";
static const string data_format_version = "0.1.0";

// section name
static const string section_name = ".esstra";

// metadata
static vector<string> allpaths;
using FileInfo = map<string, string>;
static std::map<string, FileInfo> infomap;

// hash algorithms
static const vector<string> supported_algos = {
    "md5",
    "sha256",
};
static vector<string> specified_algos;

// yaml
static const string yaml_item = "- ";
static const string yaml_indent = "  ";
static const string yaml_separator = "---";

// keys
static const string key_headers = "Headers";
static const string key_tool_name = "ToolName";
static const string key_tool_version = "ToolVersion";
static const string key_data_format_version = "DataFormatVersion";
static const string key_input_filename = "InputFileName";
static const string key_source_files = "SourceFiles";
static const string key_directory = "Directory";
static const string key_files = "Files";
static const string key_file = "File";
static const string key_md5 = "MD5";
static const string key_sha1 = "SHA1";
static const string key_sha256 = "SHA256";

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

    /*
     * Some OSes (e.g. Hurd) explicitly need to specify PATH_MAX
     * "4096" is specified in Linux, see /usr/include/linux/limits.h
     */
    #ifndef PATH_MAX
    #define PATH_MAX 4096
    #endif

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
    finfo[key_sha1] = "'" + calc_sha1(buffer, size) + "'";

    // just for demonstration
    for (const auto &algo: specified_algos) {
        debug_log("calculate '%s' hash\n", algo.c_str());
        if (algo == "md5") {
            finfo[key_md5] = "'" + calc_md5(buffer, size) + "'";
        } else if (algo == "sha256") {
            finfo[key_sha256] = "'" + calc_sha256(buffer, size) + "'";
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
    strings_to_embed.push_back(yaml_separator);

    // headers
    strings_to_embed.push_back(key_headers + ":");
    strings_to_embed.push_back(yaml_indent + key_tool_name + ": " + tool_name);
    strings_to_embed.push_back(yaml_indent + key_tool_version + ": " + tool_version);
    strings_to_embed.push_back(yaml_indent + key_data_format_version + ": " + data_format_version);
    strings_to_embed.push_back(yaml_indent + key_input_filename + ": " + main_input_filename);

    // source files
    if (allpaths.size() == 0) {
        strings_to_embed.push_back(key_source_files + ": {}");
    } else {
        strings_to_embed.push_back(key_source_files + ":");

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
            strings_to_embed.push_back(yaml_item + key_directory + ": " + directory);
            strings_to_embed.push_back(yaml_indent + key_files + ":");
            for (const auto& filename : dir_to_files[directory]) {
                debug_log("dir: %s\n", directory.c_str());
                strings_to_embed.push_back(yaml_indent + yaml_item + key_file + ": " + filename);
                string path = directory + "/" + filename;
                for (const auto& elem : infomap[path]) {
                    strings_to_embed.push_back(
                        yaml_indent + yaml_indent + elem.first + ": " + elem.second);
                }
            }
        }
    }

    // calculate size of metadata
    int datasize = 0;
    for (const auto& item : strings_to_embed) {
        datasize += item.size() + 1;  // plus 1 for null-character temination
    }
    debug_log("size=%d\n", datasize);

    // add assembly code
    fprintf(asm_out_file, "\t.pushsection %s\n", section_name.c_str());
    for (const auto& item : strings_to_embed) {
        fprintf(asm_out_file, "\t.ascii \"%s\\n\"\n", item.c_str());
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
