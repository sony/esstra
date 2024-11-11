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

#include <string>
#include <vector>
#include <map>
#include <algorithm>
#include <iostream>
#include <sstream>
#include <iomanip>

#include <stdio.h>
#include <limits.h>
#include <errno.h>

#include <unistd.h>

#include "gcc-plugin.h"
#include "output.h"
#include "plugin-version.h"

#include "lib/WjCryptLib_Md5.h"
#include "lib/WjCryptLib_Sha1.h"
#include "lib/WjCryptLib_Sha256.h"


using namespace std;

int plugin_is_GPL_compatible;

static constexpr char section_name[] = "esstra_info";

struct FileInfo {
    string abspath;
    string md5;
    string sha1;
    string sha256;
};

static vector<string> allpaths;
static map<string, FileInfo> path_to_info;


// debug log
static bool debug_mode = false;

#define DEBUG_LOG(fmt, ...) { if (debug_mode) printf("[DEBUG] " fmt, ##__VA_ARGS__); }


/*
 * convert bytes to hex string for checksums
 */
string bytes_to_hex(uint8_t *bytes, unsigned int size)
{
    stringstream hexresult;

    hexresult << std::hex << std::setfill('0');
    while (size--) {
        hexresult << (int)*bytes++;
    }

    return hexresult.str();
}

/*
 * PLUGIN_INCLUDE_FILE handler - collect paths of source files
 */
static void
collect_paths(void *gcc_data, void *user_data)
{
    string path(reinterpret_cast<const char*>(gcc_data));

    if (path[0] == '<') {
        DEBUG_LOG("skip '%s': pseudo file name\n", path.c_str());
        return;
    }

    char resolved[PATH_MAX];
    if (!realpath(path.c_str(), resolved)) {
        fprintf(stderr, "cannot get realpath from '%s'\n", path.c_str());
        perror(0);
        return;
    }

    string resolved_path(resolved);

    if (find(allpaths.begin(), allpaths.end(), resolved_path) != allpaths.end()) {
        DEBUG_LOG("skip '%s': already registered\n", resolved_path.c_str());
        return;
    }

    // calc hashes
    int fd = open(resolved_path.c_str(), O_RDONLY);
    if (fd < 0) {
        fprintf(stderr, "cannot fopen() '%s'\n", resolved_path.c_str());
        perror(0);
        return;
    }

    struct stat st;
    stat(resolved_path.c_str(), &st);
    unsigned long fsize = st.st_size;

    auto buffer = new uint8_t[fsize];
    size_t readsize = read(fd, buffer, fsize);

    if (readsize != fsize) {
        perror(0);
        return;
    }

    close(fd);

    // calc checksums
    MD5_HASH md5;
    Md5Calculate(buffer, fsize, &md5);

    SHA1_HASH sha1;
    Sha1Calculate(buffer, fsize, &sha1);

    SHA256_HASH sha256;
    Sha256Calculate(buffer, fsize, &sha256);

    // store sums to map
    FileInfo finfo = {
        string(resolved_path),
        bytes_to_hex(md5.bytes, MD5_HASH_SIZE),
        bytes_to_hex(sha1.bytes, SHA1_HASH_SIZE),
        bytes_to_hex(sha256.bytes, SHA256_HASH_SIZE),
    };
    path_to_info[resolved_path] = finfo;

    delete[] buffer;

    allpaths.push_back(resolved_path);
}

/*
 * PLUGIN_FINISH_UNIT handler - create a new ELF section and store path data in it
 */
static void
create_section(void *gcc_data, void *user_data)
{
    vector<string> metadata;

    metadata.push_back(string("InputFileName: ") + string(main_input_filename));
    for (const auto& abspath : allpaths) {
        metadata.push_back(string("SourcePath: ") + abspath);
        FileInfo& finfo = path_to_info[abspath];
        metadata.push_back(string("MD5: ") + finfo.md5);
        metadata.push_back(string("SHA1: ") + finfo.sha1);
        metadata.push_back(string("SHA256: ") + finfo.sha256);
    }

    int datasize = 0;
    for (const auto &item: metadata) {
        datasize += item.length() + 1;
    }

    int padding = 0;
    if (datasize % 4) {
        padding = 4 - datasize % 4;   // padding for 4-byte alignment
    }

    fprintf(asm_out_file, "\t.pushsection %s\n", section_name);
    fprintf(asm_out_file, "\t.balign 4\n");
    for (const auto& item : metadata) {
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
plugin_init(struct plugin_name_args *plugin_info,
            struct plugin_gcc_version *version)
{
    if (!plugin_default_version_check(version, &gcc_version)) {
        return 1;
    }

    const struct plugin_argument *argv = plugin_info->argv;
    int argc = plugin_info->argc;

    while (argc--) {
        if (strcmp(argv->key, "debug") == 0) {
            debug_mode = (atoi(argv->value) != 0);
            if (debug_mode) {
                DEBUG_LOG("debug mode enabled\n");
            }
        }
        argv++;
    }

    DEBUG_LOG("main_input_filename: %s\n", main_input_filename);

    register_callback(plugin_info->base_name,
                      PLUGIN_INCLUDE_FILE, collect_paths, 0);

    register_callback(plugin_info->base_name,
                      PLUGIN_FINISH_UNIT, create_section, 0);

    return 0;
}
