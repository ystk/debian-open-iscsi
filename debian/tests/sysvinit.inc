# Include file to support sysvinit

BASENAME=$(basename "$0")
if [ x"${BASENAME##sysvinit-}"x != x"$BASENAME"x ] ; then
  # Ignore this on Ubuntu, because sysvinit is not suppoterd there.
  if [ -f /etc/os-release ] ; then
    ( . /etc/os-release && [ x"$ID"x = x"ubuntu"x ] ) && { echo "Ignoring sysvinit-based test on Ubuntu"; exit 0; }
  elif [ -f /etc/lsb-release ] ; then
    ( . /etc/lsb-release && [ x"$DISTRIB_ID"x = x"Ubuntu"x ] ) && { echo "Ignoring sysvinit-based test on Ubuntu"; exit 0; }
  fi

  if [ x"$ADT_REBOOT_MARK"x = x"sysvinit"x ] ; then
    echo "Continuing test after sysvinit was installed."
    unset ADT_REBOOT_MARK
  elif [ -z "$ADT_REBOOT_MARK" ] ; then
    echo "Installing sysvinit and then rebooting for this test..."
    if [ -e /etc/inittab ] ; then
      # work around Debian bug #800910
      if ! grep -v ^'#' /etc/inittab | grep -vE '^[[:space:]]*$' | grep -qv ^S0 ; then
        # inittab with only serial console was created, remove it
        # before installing sysvinit (if there's a full inittab
        # present, the if condition will never be true)
        rm -f /etc/inittab
      fi
    fi

    # install sysvinit
    DEBIAN_FRONTEND=noninteractive apt-get install -y --purge sysvinit-core </dev/null

    # configure serial console if necessary
    if ! grep -q ^S0 /etc/inittab && ! grep -q ^T0 /etc/inittab ; then
      echo >> /etc/inittab
      echo "S0:23:respawn:/sbin/getty -L ttyS0 115200 vt100" >> /etc/inittab
    fi

    # reboot the system
    sync
    /tmp/autopkgtest-reboot sysvinit
  fi
fi
