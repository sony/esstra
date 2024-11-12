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

#include <stdio.h>
#include <limits.h>
#include <errno.h>

#include "gcc-plugin.h"
#include "output.h"
#include "plugin-version.h"


int plugin_is_GPL_compatible;

static std::vector<std::string> allpaths;

static constexpr char section_name[] = "esstra_info";

static constexpr char tag_input_filename[] = "InputFileName: ";
static constexpr char tag_source_path[] = "SourcePath: ";

static bool debug_mode = false;

/*
 * debug print
 */
static void
debug_log(char const* format, ...) {
    if (debug_mode) {
        va_list args;
        va_start(args, format);
        printf("[DEBUG] ");
        vprintf(format, args);
        va_end(args);
    }
}


/*
 * PLUGIN_INCLUDE_FILE handler - collect paths of source files
 */
static void
collect_paths(void *gcc_data, void *user_data) {
    std::string path(reinterpret_cast<const char*>(gcc_data));

    if (path[0] == '<') {
        debug_log("skip '%s': pseudo file name\n", path.c_str());
        return;
    }

    char resolved[PATH_MAX];
    if (!realpath(path.c_str(), resolved)) {
        fprintf(stderr, "cannot get realpath from '%s'\n", path.c_str());
        perror(0);
        return;
    }

    std::string resolved_path(resolved);

    if (find(allpaths.begin(), allpaths.end(), resolved_path) != allpaths.end()) {
        debug_log("skip '%s': already registered\n", resolved_path.c_str());
        return;
    }

    allpaths.push_back(resolved_path);
}

/*
 * PLUGIN_FINISH_UNIT handler - create a new ELF section and store path data in it
 */
static void
create_section(void *gcc_data, void *user_data) {
    std::vector<std::string> strings_to_embed;

    // construct metadata
    strings_to_embed.push_back(tag_input_filename + std::string(main_input_filename));
    for (const auto& path : allpaths) {
        strings_to_embed.push_back(tag_source_path + std::string(path));
    }

    // calculate size of metadata
    int datasize = 0;
    for (const auto& item : strings_to_embed) {
        datasize += item.size() + 1; // plus 1 for null-character temination
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
plugin_init(struct plugin_name_args *plugin_info,
            struct plugin_gcc_version *version) {
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
