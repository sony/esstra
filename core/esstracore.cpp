/* SPDX-License-Identifier: GPL-3.0-or-later
 *
 * Copyright 2024 Sony Group Corporation
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

#include <string>
#include <vector>
#include <map>
#include <algorithm>
#include <iostream>
#include <iomanip>

#include "gcc-plugin.h"
#include "output.h"
#include "plugin-version.h"

#include "lib/WjCryptLib_Aes.h"
#include "lib/WjCryptLib_AesCbc.h"
#include "lib/WjCryptLib_AesCtr.h"
#include "lib/WjCryptLib_AesOfb.h"
#include "lib/WjCryptLib_Md5.h"
#include "lib/WjCryptLib_Rc4.h"
#include "lib/WjCryptLib_Sha1.h"
#include "lib/WjCryptLib_Sha256.h"
#include "lib/WjCryptLib_Sha512.h"


using std::vector;
using std::string;
using std::map;
using std::stringstream;


int plugin_is_GPL_compatible;


// metadata
static constexpr char section_name[] = "esstra_info";
static vector<string> allpaths;
struct FileInfo {
    map<string, string> checksums;
};
static std::map<string, FileInfo> infomap;

// hash algorithms
static constexpr const char* algos[] = {
    "aes",
    "aescbc",
    "aesctr",
    "aesofb",
    "md5",
    "rc4",
    "sha1",
    "sha256",
    "sha512",
};
static vector<string> specified_algos;


// tags
static constexpr char tag_input_filename[] = "InputFileName: ";
static constexpr char tag_source_path[] = "SourcePath: ";
static constexpr char tag_checksum[] = "Checksum: ";

// debugging
static bool debug_mode = false;

/*
 * debug print
 */
static void
debug_log(const char* format, ...) {
    if (debug_mode) {
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
// static string
// bytes_to_string(uint8_t* bytes, unsigned size) {
//     stringstream hexstream;
//     hexstream << std::hex << std::setfill('0');
//     while (size--) {
//         hexstream << static_cast<int>(*bytes++);
//     }
//     return hexstream.str();
// }

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

    MD5_HASH md5sum;
    Md5Calculate(buffer, size, &md5sum);

    // // store to map
    // FileInfo finfo;
    // string md5string = bytes_to_string(md5sum.bytes, MD5_HASH_SIZE);
    // finfo.md5sum = "MD5: " + md5string;
    // infomap[resolved_path] = finfo;

    delete[] buffer;
}

/*
 * PLUGIN_FINISH_UNIT handler - create a new ELF section and store path data in it
 */
static void
create_section(void* /* gcc_data */, void* /* user_data */) {
    vector<string> strings_to_embed;

    // construct metadata
    strings_to_embed.push_back(tag_input_filename + string(main_input_filename));
    for (const auto& path : allpaths) {
        strings_to_embed.push_back(tag_source_path + string(path));
        // strings_to_embed.push_back(tag_checksum + infomap[path].md5sum);
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
        fprintf(asm_out_file, "\t.asciz \"%s\"\n", item.c_str());
    }
    if (padding > 0) {
        fprintf(asm_out_file, "\t.dcb %d\n", padding);
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

    const struct plugin_argument *argv = plugin_info->argv;
    int argc = plugin_info->argc;

    while (argc--) {
        if (strcmp(argv->key, "debug") == 0) {
            debug_mode = (atoi(argv->value) != 0);
            if (debug_mode) {
                debug_log("debug mode enabled\n");
            }
        } else if (strcmp(argv->key, "checksum") == 0) {
            debug_log("arg-checksum: %s\n", argv->value);
            auto value = reinterpret_cast<const char*>(argv->value);
            stringstream ss_checksum;
            string algo;
            while (*value) {
                if (*value == ',') {
                    algo = ss_checksum.str();
                    if (algo.length() > 0) {
                        specified_algos.push_back(algo);
                        algo = "";
                    }
                    ss_checksum.str("");
                    ss_checksum.clear(stringstream::goodbit);
                } else {
                    ss_checksum << *value;
                }
                value++;
            }
            algo = ss_checksum.str();
            if (algo.length() > 0) {
                specified_algos.push_back(algo);
            }
            // show all algos
            for (auto& algo: specified_algos)
                debug_log("algo: '%s'\n", algo.c_str());
        }
        argv++;
    }

    debug_log("main_input_filename: %s\n", main_input_filename);

    register_callback(plugin_info->base_name,
                      PLUGIN_INCLUDE_FILE, collect_paths, 0);

    register_callback(plugin_info->base_name,
                      PLUGIN_FINISH_UNIT, create_section, 0);

    return 0;
}
