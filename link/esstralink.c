/*
 * SPDX-FileCopyrightText: Copyright 2025 Sony Group Corporation
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
#include <inttypes.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <sys/wait.h>
#include <linux/limits.h>
#include "plugin-api.h"

static const char *tool_name = "ESSTRA Link";
static const char *tool_version = "0.4.0";

static ld_plugin_message message;
static const char *link_output_name = NULL;
static ld_plugin_register_cleanup register_cleanup;

#define FILE_PREFIX_MAP_OPTION "file-prefix-map="
#define FILE_PREFIX_MAP_DELIMITER ":"
static char shrink_option[] = "--file-prefix-map";
static char shrink_value[ARG_MAX - sizeof(shrink_option) - 1];

/*
 * CLEANUP HOOK - aggregates metadata
 */
static enum ld_plugin_status
oncleanup(void)
{
    message(LDPL_INFO, "[%s] now aggregating metadata in '%s'...", tool_name, link_output_name);

    char buf[256];

    pid_t pid = fork();
    if (pid < 0) {
        message(LDPL_FATAL, "[%s] fork failed: %s", tool_name, strerror_r(errno, buf, sizeof(buf)));
        return LDPS_ERR;
    }

    if (pid == 0) {
        // child process
        char filename[PATH_MAX];
        char option[ARG_MAX];
        snprintf(option, sizeof(option), "%s=%s", shrink_option, shrink_value);
        strncpy(filename, link_output_name, PATH_MAX - 1);
        char *args[] = {"esstra", "shrink", option, filename, NULL};
        message(LDPL_INFO, "[%s] invoking: '%s %s %s %s'...",
                tool_name, args[0], args[1], args[2], args[3]);
        execvp("esstra", args);
        // below runs only on error
        message(LDPL_FATAL, "[%s] execvp failed: %s", tool_name, strerror_r(errno, buf, sizeof(buf)));
        return LDPS_ERR;
    } else {
        // just wait until child process finishes
        wait(NULL);
    }
    message(LDPL_INFO, "[%s] metadata in '%s' successfully updated", tool_name, link_output_name);

    return LDPS_OK;
}

/*
 * ld plugin initialization
 */
enum ld_plugin_status
onload(struct ld_plugin_tv *tv)
{
    struct ld_plugin_tv *p;
    enum ld_plugin_status status;

    fprintf(stderr, "[%s] loaded: v%s\n", tool_name, tool_version);

    p = tv;

    while (p->tv_tag) {
        switch (p->tv_tag) {
        case LDPT_MESSAGE:
            message = p->tv_u.tv_message;
            status = LDPS_OK;
            break;
        case LDPT_REGISTER_CLEANUP_HOOK:
            register_cleanup = p->tv_u.tv_register_cleanup;
            status = register_cleanup(oncleanup);
            if (status != LDPS_OK) {
                message(LDPL_FATAL, "[%s] register cleanup hook failed", tool_name);
                return status;
            }
            break;
        case LDPT_OUTPUT_NAME:
            link_output_name = p->tv_u.tv_string;
            status = LDPS_OK;
            break;
        case LDPT_OPTION:
            const char *option = p->tv_u.tv_string;
            message(LDPL_INFO, "option [%s]", option);
            if (strncmp(option, FILE_PREFIX_MAP_OPTION, strlen(option)) != 0) {
                message(LDPL_FATAL, "[%s] invalid option", option);
                return LDPS_ERR;
            }
            if (strlen(shrink_value) > 0) {
                strncat(shrink_value, " ", sizeof(shrink_value));
            }
            size_t remaining = sizeof(shrink_value) - strlen(shrink_value) - 1;
            strncat(shrink_value, option + strlen(FILE_PREFIX_MAP_OPTION), remaining);
            message(LDPL_INFO, "shrink_value: '%s'", shrink_value);
            status = LDPS_OK;
            break;
        default:
            break;
        }
        p++;
    }

    return status;
}
