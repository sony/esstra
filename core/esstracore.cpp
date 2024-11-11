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

using namespace std;

int plugin_is_GPL_compatible;

static constexpr char section_name[] = "esstra_info";

static vector<string> allpaths;


// debug log
static bool debug_mode = false;

#define DEBUG_LOG(fmt, ...) { if (debug_mode) printf("[DEBUG] " fmt, ##__VA_ARGS__); }


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

    allpaths.push_back(resolved_path);
}

/*
 * PLUGIN_FINISH_UNIT handler - create a new ELF section and store path data in it
 */
static void
create_section(void *gcc_data, void *user_data)
{
    // +3 for '[', ']' and '\0'
    int datasize = strlen(main_input_filename) + 3;

    for (const auto& path : allpaths) {
        datasize += path.size() + 1;  // +1 for '\0' at the end of each c-string
    }

    int padding = 0;
    if (datasize % 4) {
        padding = 4 - datasize % 4;   // padding for 4-byte alignment
    }

    fprintf(asm_out_file, "\t.pushsection %s\n", section_name);
    fprintf(asm_out_file, "\t.balign 4\n");
    fprintf(asm_out_file, "\t.asciz \"<%s>\"\n", main_input_filename);
    for (const auto& pathinfo : allpaths) {
        fprintf(asm_out_file, "\t.asciz \"%s\"\n", pathinfo.c_str());
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
