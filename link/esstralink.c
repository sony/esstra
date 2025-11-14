// SPDX-FileCopyrightText: Copyright 2025 Sony Group Corporation
// SPDX-License-Identifier: GPL-3.0-or-later

#include <stdio.h>
#include <inttypes.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <stdbool.h>
#include <sys/wait.h>
#include <linux/limits.h>
#include "plugin-api.h"

#ifndef PATH_MAX
#define PATH_MAX 4096
#endif

#ifndef ARG_MAX
#define ARG_MAX 4096
#endif

static const char *tool_name = "ESSTRA Link";
static const char *tool_version = "0.5.0";

static ld_plugin_message message;
static const char *link_output_name = NULL;

#define ESSTRA_UTIL_COMMAND "esstra"
#define FILE_PREFIX_MAP_OPTION "file-prefix-map="
#define FILE_PREFIX_MAP_DELIMITER ":"
static bool exists_shrink_option = false;
static char shrink_rule[ARG_MAX - sizeof(FILE_PREFIX_MAP_OPTION) - 2]; /* '2' is for '=' and '\0' */


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

    int retcode = LDPS_OK;

    if (pid == 0) {
        // child process
        char filename[PATH_MAX];
        strncpy(filename, link_output_name, PATH_MAX - 1);
        if (exists_shrink_option) {
            char option[ARG_MAX];
            snprintf(option, sizeof(option), "--%s%s", FILE_PREFIX_MAP_OPTION, shrink_rule);
            char *args[] = {"esstra", "shrink", option, filename, NULL};
            message(LDPL_INFO, "[%s] invoking: '%s %s %s %s'...",
                    tool_name, args[0], args[1], args[2], args[3]);
            execvp(ESSTRA_UTIL_COMMAND, args);
        } else {
            char *args[] = {"esstra", "shrink", filename, NULL};
            message(LDPL_INFO, "[%s] invoking: '%s %s %s'...",
                    tool_name, args[0], args[1], args[2]);
            execvp(ESSTRA_UTIL_COMMAND, args);
        }
        // below runs only on error
        message(LDPL_FATAL, "[%s] execvp failed: %s", tool_name, strerror_r(errno, buf, sizeof(buf)));
        exit(1);
    } else {
        int status;
        waitpid(pid, &status, 0);
        if (WIFEXITED(status)) {
            int exitcode = WEXITSTATUS(status);
            if (exitcode == 0) {
                message(LDPL_INFO, "[%s] metadata in '%s' successfully updated", tool_name, link_output_name);
            } else {
                retcode = LDPS_ERR;
            }
        }
    }
    return retcode;
}

/*
 * ld plugin initialization
 */
enum ld_plugin_status
onload(struct ld_plugin_tv *tv)
{
    struct ld_plugin_tv *p;
    enum ld_plugin_status status;
    ld_plugin_register_cleanup register_cleanup = NULL;

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
            status = LDPS_OK;
            break;
        case LDPT_OUTPUT_NAME:
            link_output_name = p->tv_u.tv_string;
            status = LDPS_OK;
            break;
        case LDPT_OPTION:
            const char *option = p->tv_u.tv_string;
            // message(LDPL_INFO, "option [%s]", option);
            if (strncmp(option, FILE_PREFIX_MAP_OPTION, strlen(FILE_PREFIX_MAP_OPTION)) != 0) {
                message(LDPL_FATAL, "[%s] invalid option", option);
                return LDPS_ERR;
            }
            exists_shrink_option = true;
            size_t remaining = sizeof(shrink_rule) - strlen(shrink_rule) - 1;
            strncat(shrink_rule, option + strlen(FILE_PREFIX_MAP_OPTION), remaining);
            // message(LDPL_INFO, "shrink_rule: '%s'", shrink_rule);
            status = LDPS_OK;
            break;
        default:
            break;
        }
        p++;
    }

    if (register_cleanup) {
        status = register_cleanup(oncleanup);
        if (status != LDPS_OK) {
            message(LDPL_FATAL, "[%s] register cleanup hook failed", tool_name);
            return status;
        }
    }

    return status;
}
