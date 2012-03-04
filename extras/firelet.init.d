#!/bin/sh
#
# init.d script with LSB support.
#
# Copyright (c) 2011 Federico Ceratto <federico.ceratto@gmail.com>
#
# This is free software; you may redistribute it and/or modify
# it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2,
# or (at your option) any later version.
#
# This is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License with
# the Debian operating system, in /usr/share/common-licenses/GPL;  if
# not, write to the Free Software Foundation, Inc., 59 Temple Place,
# Suite 330, Boston, MA 02111-1307 USA
#
### BEGIN INIT INFO
# Provides:          firelet
# Required-Start:    $network $local_fs
# Required-Stop:     $network $local_fs
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Firelet Webapp Daemon
# Description:       Firewall management
### END INIT INFO

# Author: Federico Ceratto <federico.ceratto@gmail.com>

CONF=/etc/firelet/firelet.ini
DAEMON=/usr/bin/fireletd
DAEMONUSER=${DAEMONUSER:-firelet}
DESC="Firelet Webapp Daemon"
NAME=firelet
PATH=/sbin:/usr/sbin:/bin:/usr/bin
PIDFILE=/var/run/$NAME.pid
RUNPATH=/usr/share/firelet/
SCRIPTNAME=/etc/init.d/$NAME
# Arguments to run the daemon with:
#  --cf <configuation_file_name>
#  -o <run_directory>
#  --daemonize <pid_file_name>
#DAEMON_ARGS="--cf $CONF -o $RUNPATH --daemonize --pidfile $PIDFILE"
DAEMON_ARGS="--cf $CONF -o $RUNPATH"
GIT_REPO_DIR=/var/lib/firelet

# Exit if the package is not installed
[ -x $DAEMON ] || exit 0

# Read configuration variable file if it is present
[ -r /etc/default/$NAME ] && . /etc/default/$NAME

# Load the VERBOSE setting and other rcS variables
. /lib/init/vars.sh

# Define LSB log_* functions.
# Depend on lsb-base (>= 3.0-6) to ensure that this file is present.
. /lib/lsb/init-functions

#
# Function that starts the daemon/service
#
do_start()
{
    # Return
    #   0 if daemon has been started
    #   1 if daemon was already running
    #   2 if daemon could not be started
    get_status;
    if [ "$?" != 1 ]; then
        echo -n "Error: "
        do_status
        return 1
    fi
    start-stop-daemon --start --quiet --pidfile $PIDFILE --chdir $RUNPATH \
        --background --make-pidfile \
        --chuid $DAEMONUSER --exec $DAEMON -- $DAEMON_ARGS || return 2
}

#
# Function that stops the daemon/service
#
do_stop()
{
    # Return
    #   0 if daemon has been stopped
    #   1 if daemon was already stopped
    #   2 if daemon could not be stopped
    #   other if a failure occurred
    get_status;
    if [ "$?" != 0 ]; then
        echo -n "Error: "
        do_status
        return 2
    fi
    start-stop-daemon --stop --quiet --retry=TERM/30/KILL/5 --chuid $DAEMONUSER \
        --pidfile $PIDFILE --name $NAME
    RETVAL="$?"
    [ "$RETVAL" = 2 ] && return 2
    # Wait for children to finish too if this is a daemon that forks
    # and if the daemon is only ever run from this initscript.
    # If the above conditions are not satisfied then add some other code
    # that waits for the process to drop all resources that could be
    # needed by services started subsequently.  A last resort is to
    # sleep for some time.
    start-stop-daemon --stop --quiet --oknodo --retry=0/30/KILL/5 --exec $DAEMON
    [ "$?" = 2 ] && return 2
    # Many daemons don't delete their pidfiles when they exit.
    rm -f $PIDFILE
    return "$RETVAL"
}

is_up() {
    pidof $NAME >/dev/null; return "$?";
}

get_status() {
    [ -f $PIDFILE ] && is_up && return 0;
    [ ! -f $PIDFILE ] && ! is_up && return 1;
    [ -f $PIDFILE ] && ! is_up && return 3;
    [ ! -f $PIDFILE ] && is_up && return 4;
}

do_status() {
    get_status; STATUS="$?";
    case "$STATUS" in
        0) log_success_msg "$NAME is running";;
        1) log_failure_msg "$NAME is not running";;
        3) log_failure_msg "$NAME is not running but $PIDFILE is present";;
        4) log_failure_msg "$NAME is running but $PIDFILE is not present";;
    esac
    return $STATUS;
}

#
# Function that sends a SIGHUP to the daemon/service
#
do_reload() {
    #
    # If the daemon can reload its configuration without
    # restarting (for example, when it is sent a SIGHUP),
    # then implement that here.
    #
    start-stop-daemon --stop --signal 1 --quiet --pidfile $PIDFILE --name $NAME
    return 0
}

#
# Perform git repository backup if configured
#
do_backup() {
    # Return
    #   0 backups has been completed
    #   1 otherwise
    echo "Checking $GIT_REPO_DIR directory"
    if [ ! -d $GIT_REPO_DIR ]; then
        echo "Error: $GIT_REPO_DIR does not exists"
        return 1
    fi
    cd $GIT_REPO_DIR

    echo "Checking Git repository"
    if [ ! -d .git ]; then
        echo "Error: $GIT_REPO_DIR is not a Git repository"
        return 1
    fi

    echo "Checking Git remotes"
    remotes=$(git remote show | grep ^backup)
    if [ ! $remotes ]; then
        echo "Error: no remotes configured in Git, please refer to Backup documentation"
        return 1
    fi

    echo "Performing backups"
    for remote in $remotes; do
        echo "Executing: git push $remote"
        git push $remote
        RETVAL="$?"
        if [ "$RETVAL" != 0 ]; then
            echo "Failed git push"
            return 1
        fi
        echo "Done"
    done

    log_daemon_msg "Backup completed"
    return 0
}



case "$1" in
  start)
    [ "$VERBOSE" != no ] && log_daemon_msg "Starting $DESC " "$NAME"
    do_start
    case "$?" in
        0|1) [ "$VERBOSE" != no ] && log_end_msg 0 ;;
        2) [ "$VERBOSE" != no ] && log_end_msg 1 ;;
    esac
  ;;
  stop)
    [ "$VERBOSE" != no ] && log_daemon_msg "Stopping $DESC" "$NAME"
    do_stop
    case "$?" in
        0|1) [ "$VERBOSE" != no ] && log_end_msg 0 ;;
        2) [ "$VERBOSE" != no ] && log_end_msg 1 ;;
    esac
    ;;
  status)
       do_status || exit $?
       ;;
  #reload|force-reload)
    #
    # If do_reload() is not implemented then leave this commented out
    # and leave 'force-reload' as an alias for 'restart'.
    #
    #log_daemon_msg "Reloading $DESC" "$NAME"
    #do_reload
    #log_end_msg $?
    #;;
  restart|force-reload)
    #
    # If the "reload" option is implemented then remove the
    # 'force-reload' alias
    #
    log_daemon_msg "Restarting $DESC" "$NAME"
    do_stop
    case "$?" in
      0|1)
        do_start
        case "$?" in
            0) log_end_msg 0 ;;
            1) log_end_msg 1 ;; # Old process is still running
            *) log_end_msg 1 ;; # Failed to start
        esac
        ;;
      *)
        # Failed to stop
        log_end_msg 1
        ;;
    esac
    ;;
  backup)
    do_backup
        case "$?" in
            0) log_end_msg 0 ;; # Success
            1) log_end_msg 1 ;; # Failed to run
            *) log_end_msg 1 ;; # Failed to run
        esac
    ;;
  *)
    #echo "Usage: $SCRIPTNAME {start|stop|restart|reload|force-reload}" >&2
    echo "Usage: $SCRIPTNAME {start|stop|status|restart|force-reload|backup}" >&2
    exit 3
    ;;
esac

:
