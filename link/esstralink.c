// SPDX-FileCopyrightText: Copyright 2025 Sony Group Corporation
// SPDX-License-Identifier: GPL-3.0-or-later

#include <stdio.h>
#include <inttypes.h>
#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <stdbool.h>
#include <stdarg.h>
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

static ld_plugin_message plugin_message = NULL;
static const char *link_output_name = NULL;

#define ESSTRA_UTIL_COMMAND "esstra"
#define FILE_PREFIX_MAP_OPTION "file-prefix-map="
#define FILE_PREFIX_MAP_DELIMITER ":"
static bool exists_shrink_option = false;
static char shrink_rule[ARG_MAX - sizeof(FILE_PREFIX_MAP_OPTION) - 2]; /* '2' is for '=' and '\0' */

enum MessageLevel {
    L_DEBUG  = 1U,
    L_INFO   = 1U << 2,
    L_NOTICE = 1U << 3,
    L_ERROR  = 1U << 4,
};
static uint8_t messages_to_show = L_ERROR | L_NOTICE;
#define MSG_LEN 1024

/*
 * message
 */
static void
message(enum MessageLevel level, const char* format, ...) {
    if (plugin_message == NULL) return;
    if ((messages_to_show & level) == 0) return;

    char msg[MSG_LEN];
    va_list args;
    va_start(args, format);
    vsnprintf(msg, MSG_LEN, format, args);
    va_end(args);

    (void)tool_version;
    enum ld_plugin_level lv = level & L_ERROR ? LDPL_ERROR : LDPL_INFO;
    plugin_message(lv, msg);
}


/*
 * CLEANUP HOOK - aggregates metadata
 */
static enum ld_plugin_status
oncleanup(void)
{
    message(L_INFO, "[%s] now optimizing metadata in '%s'...", tool_name, link_output_name);

    char buf[256];

    pid_t pid = fork();
    if (pid < 0) {
        message(L_ERROR, "[%s] fork failed: %s", tool_name, strerror_r(errno, buf, sizeof(buf)));
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
            message(L_DEBUG, "> invoking: '%s %s %s %s'...", args[0], args[1], args[2], args[3]);
            execvp(ESSTRA_UTIL_COMMAND, args);
        } else {
            char *args[] = {"esstra", "shrink", filename, NULL};
            message(L_DEBUG, "> invoking: '%s %s %s'...", args[0], args[1], args[2]);
            execvp(ESSTRA_UTIL_COMMAND, args);
        }
        // below runs only on error
        message(L_ERROR, "[%s] execvp failed: %s", tool_name, strerror_r(errno, buf, sizeof(buf)));
        exit(1);
    } else {
        int status;
        waitpid(pid, &status, 0);
        if (WIFEXITED(status)) {
            int exitcode = WEXITSTATUS(status);
            message(L_DEBUG, "> 'esstra shrink' exited with code %d", exitcode);
            if (exitcode == 0) {
                message(L_INFO, "[%s] metadata in '%s' successfully updated", tool_name, link_output_name);
            } else {
                message(L_ERROR, "[%s] ESSTRA Utility failed with code %d",
                        tool_name, link_output_name, exitcode);
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

    p = tv;

    while (p->tv_tag) {
        switch (p->tv_tag) {
        case LDPT_MESSAGE:
            plugin_message = p->tv_u.tv_message;
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
        {
            const char *option = p->tv_u.tv_string;
            message(L_DEBUG, "> option '%s'", option);
            if (strncmp(option, FILE_PREFIX_MAP_OPTION, strlen(FILE_PREFIX_MAP_OPTION)) == 0) {
                exists_shrink_option = true;
                size_t remaining = sizeof(shrink_rule) - strlen(shrink_rule) - 1;
                strncat(shrink_rule, option + strlen(FILE_PREFIX_MAP_OPTION), remaining);
                message(L_DEBUG, "> shrink_rule: '%s'", shrink_rule);
                status = LDPS_OK;
            } else if (strcmp(option, "debug") == 0) {
                messages_to_show |= L_DEBUG | L_ERROR | L_NOTICE | L_INFO;
                message(L_DEBUG, "> debug mode enabled");
            } else if (strcmp(option, "verbose") == 0) {
                messages_to_show |= L_ERROR | L_NOTICE | L_INFO;
                message(L_DEBUG, "> verbose mode enabled");
            } else if (strcmp(option, "silent") == 0) {
                messages_to_show &= ~(L_ERROR | L_INFO | L_DEBUG);
                message(L_DEBUG, "> silent mode enabled");
            } else if (strcmp(option, "show-error") == 0) {
                messages_to_show |= L_ERROR;
                message(L_DEBUG, "> show errors");
            } else {
                message(L_ERROR, "[%s] invalid option: '%s'", tool_name, option);
                return LDPS_ERR;
            }
            break;
        }

        default:
            break;
        }
        p++;
    }

    if (register_cleanup) {
        status = register_cleanup(oncleanup);
        if (status != LDPS_OK) {
            message(L_ERROR, "[%s] register cleanup hook failed", tool_name);
            return status;
        }
    }

    message(L_INFO, "[%s] loaded: %s", tool_name, tool_version);

    return status;
}
