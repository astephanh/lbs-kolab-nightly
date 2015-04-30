# Needed for opensuse build system
%if 0%{?opensuse_bs}
#!BuildIgnore:  boa
#!BuildIgnore:  cherokee
#!BuildIgnore:  nginx
#!BuildIgnore:  httpd-itk
#!BuildIgnore:  lighttpd
#!BuildIgnore:  thttpd

#!BuildIgnore:  fedora-logos-httpd

#!BuildIgnore:  php-mysqlnd

#!BuildIgnore:  roundcubemail-skin-classic
#!BuildIgnore:  roundcubemail-plugin-jqueryui-skin-classic
%endif

%{!?php_inidir: %global php_inidir %{_sysconfdir}/php.d}

%if 0%{?suse_version}
%global httpd_group www
%global httpd_name apache2
%global httpd_user wwwrun
%else
%global httpd_group apache
%global httpd_name httpd
%global httpd_user apache
%endif

%global _ap_sysconfdir %{_sysconfdir}/%{httpd_name}

Name:           kolab-syncroton
Version:        2.3.2
Release:        99.dev%(date +%%Y%%m%%d)%{?dist}
Summary:        ActiveSync for Kolab Groupware

Group:          Applications/Internet
License:        LGPLv2
URL:            http://www.syncroton.org

Source0:        kolab-syncroton-master.tar.gz
Source1:        kolab-syncroton.logrotate

BuildArch:      noarch

# Use this build requirement to make sure we are using
# up to date vendorized copies of the plugins.
BuildRequires:  roundcubemail-plugin-kolab_auth >= 3.2
BuildRequires:  roundcubemail-plugin-kolab_folders >= 3.2
BuildRequires:  roundcubemail-plugin-libkolab >= 3.2

%if 0%{?suse_version}
BuildRequires:  roundcubemail
Requires:       php
Requires:       php-pear-Auth_SASL
Requires:       php-pear-MDB2_Driver_mysqli
Requires:       php-pear-Net_IDNA2
Requires:       php-pear-Net_SMTP
Requires:       php-pear-Net_Socket
%else
Requires:       php-common >= 5.3
Requires:       php-pear-Auth-SASL
Requires:       php-pear-MDB2-Driver-mysqli
Requires:       php-pear-Net-IDNA2
Requires:       php-pear-Net-SMTP
Requires:       php-pear-Net-Socket
%endif

Requires:       logrotate
Requires:       roundcubemail(core)
Requires:       roundcubemail-plugin-kolab_auth >= 3.2
Requires:       roundcubemail-plugin-kolab_folders >= 3.2
Requires:       roundcubemail-plugin-libkolab >= 3.2
Requires:       php-kolabformat
Requires:       php-pear-MDB2
Requires:       php-ZendFramework

%description
Kolab Groupware provides ActiveSync for Calendars, Address Books
and Tasks though this package - based on Syncroton technology.

%prep
%setup -q -n kolab-syncroton-master

rm -rf \
    lib/ext/Auth/ \
    lib/ext/MDB2/ \
    lib/ext/MDB2.php \
    lib/ext/Net/IDNA2/ \
    lib/ext/Net/IDNA2.php \
    lib/ext/Net/SMTP.php \
    lib/ext/Net/Socket.php \
    lib/ext/Roundcube/ \
    lib/ext/Zend/ \
    lib/plugins/

%build

%install
mkdir -p \
    %{buildroot}/%{_datadir}/%{name} \
    %{buildroot}/%{_ap_sysconfdir}/conf.d/ \
    %{buildroot}/%{_sysconfdir}/%{name} \
    %{buildroot}/%{_var}/log/%{name}

mkdir -p %{buildroot}%{_sysconfdir}/logrotate.d
cp -pr %SOURCE1 %{buildroot}%{_sysconfdir}/logrotate.d/kolab-syncroton

cp -a lib %{buildroot}/%{_datadir}/%{name}/.
cp -a index.php %{buildroot}/%{_datadir}/%{name}/.

pushd %{buildroot}/%{_datadir}/%{name}
ln -s ../../..%{_sysconfdir}/roundcubemail config
ln -s ../../..%{_var}/log/%{name} logs
pushd lib/ext
ln -s ../../../roundcubemail/program/lib/Roundcube
popd
for plugin in kolab_auth kolab_folders libkolab; do
    mkdir -p lib/plugins/$plugin
    pushd lib/plugins/$plugin
    if [ -d "/usr/share/roundcubemail/plugins/" ]; then
        find /usr/share/roundcubemail/plugins/$plugin/ -mindepth 1 -maxdepth 1 ! -name "config.inc.php" | while read link_target; do
            ln -sv "$(echo ${link_target} | sed -e 's|/usr/share/roundcubemail/|../../../../roundcubemail/|g')"
        done
    else
        find ../../../../roundcubemail/plugins/$plugin/ -mindepth 1 -maxdepth 1 ! -name "config.inc.php" -exec ln -sv {} \;
    fi
    popd
done
popd

# Kolab Authentication plugin
pushd %{buildroot}/%{_datadir}/%{name}/lib/plugins/kolab_auth
rm -rf config.inc.php.dist
ln -s ../../../../../..%{_sysconfdir}/roundcubemail/kolab_auth.inc.php config.inc.php
popd

# Kolab Folders plugin
pushd %{buildroot}/%{_datadir}/%{name}/lib/plugins/kolab_folders
rm -rf config.inc.php.dist
ln -s ../../../../../..%{_sysconfdir}/roundcubemail/kolab_folders.inc.php config.inc.php
popd

# Libkolab plugin
pushd %{buildroot}/%{_datadir}/%{name}/lib/plugins/libkolab
rm -rf config.inc.php.dist
ln -s ../../../../../..%{_sysconfdir}/roundcubemail/libkolab.inc.php config.inc.php
popd

cp -a docs/kolab-syncroton.conf %{buildroot}/%{_ap_sysconfdir}/conf.d/

find %{buildroot}/%{_datadir}/%{name}/ -type f -name "*.orig" -delete

# Fix anything executable that does not have a shebang
for file in `find %{buildroot}/%{_datadir}/%{name}/ -type f -perm /a+x`; do
    [ -z "`head -n 1 $file | grep \"^#!/\"`" ] && chmod -v 644 $file
done

# Find files with a shebang that do not have executable permissions
for file in `find %{buildroot}/%{_datadir}/%{name}/ -type f ! -perm /a+x`; do
    [ ! -z "`head -n 1 $file | grep \"^#!/\"`" ] && chmod -v 755 $file
done

# Find files that have non-standard-executable-perm
find %{buildroot}/%{_datadir}/%{name}/ -type f -perm /g+wx -exec chmod -v g-w {} \;

# Find files that are not readable
find %{buildroot}/%{_datadir}/%{name}/ -type f ! -perm /go+r -exec chmod -v go+r {} \;

%pre
if [ -d "/usr/share/kolab-syncroton/lib/ext/Roundcube" -a ! -L "/usr/share/kolab-syncroton/lib/ext/Roundcube" ]; then
    rm -rf "/usr/share/kolab-syncroton/lib/ext/Roundcube"
fi
if [ -d "/usr/share/kolab-syncroton/lib/plugins/" ]; then
    find /usr/share/kolab-syncroton/lib/plugins/ -mindepth 2 -maxdepth 2 | while read file; do
        if [ ! -L "${file}" ]; then
            rm -rf "${file}"
        fi
    done
fi

%post
if [ -f "%{php_inidir}/apc.ini" ]; then
    if [ ! -z "`grep ^apc.enabled=1 %{php_inidir}/apc.ini`" ]; then
%if 0%{?fedora} > 15
        /bin/systemctl condrestart %{httpd_name}.service
%else
        /sbin/service %{httpd_name} condrestart
%endif
    fi
fi

/usr/share/roundcubemail/bin/updatedb.sh \
    --dir /usr/share/doc/kolab-syncroton-%{version}/SQL/ \
    --package syncroton \
    >/dev/null 2>&1 || :

exit 0

%files
%doc docs/*
%if 0%{?suse_version}
%dir %{_ap_sysconfdir}/
%dir %{_ap_sysconfdir}/conf.d/
%endif
%config(noreplace) %{_ap_sysconfdir}/conf.d/kolab-syncroton.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%{_datadir}/%{name}
%attr(0770,%{httpd_user},%{httpd_group}) %{_var}/log/%{name}

%changelog
* Fri Mar 27 2015 Jeroen van Meeuwen (Kolab Systems) <vanmeeuwen@kolabsys.com> - 2.3.2-1
- Release of version 2.3.2, see;

  https://issues.kolab.org/buglist.cgi?target_milestone=2.3.2&product=Syncroton

* Thu Feb  5 2015 Jeroen van Meeuwen (Kolab Systems) <vanmeeuwen@kolabsys.com> - 2.3.1-1
- Release of version 2.3.1, see;

  https://issues.kolab.org/buglist.cgi?target_milestone=2.3.1&product=Syncroton

* Tue Jan 27 2015 Jeroen van Meeuwen (Kolab Systems) <vanmeeuwen@kolabsys.com> - 2.3.0-1
- Release of version 2.3.0, see;

  https://issues.kolab.org/buglist.cgi?target_milestone=2.3.0&product=Syncroton

* Mon Sep 15 2014 Daniel Hoffend <dh@dotlan.net> - 2.3-0.2.git
- New upstream version

* Tue Apr  8 2014 Jeroen van Meeuwen (Kolab Systems) <vanmeeuwen@kolabsys.com> - 2.2.5-2
- Include fix for From: header off iOS devices

* Sun Apr  6 2014 Jeroen van Meeuwen (Kolab Systems) <vanmeeuwen@kolabsys.com> - 2.2.5-1
- New upstream version
- #2664 - Fix for devices that do not support empty Sync responses
- Fix synchronization of task importance
- #2845 - Fix invalid email message identifier in Move response
- Fix issues in recode_message() - wrong boundaries handling

* Tue Feb 11 2014 Jeroen van Meeuwen (Kolab Systems) <vanmeeuwen@kolabsys.com> - 2.2.4-5
- Rebuild against up-to-date roundcubemail-plugins-kolab
- Fix memory consumption issues on very large result sets (#2828)

* Thu Feb  6 2014 Jeroen van Meeuwen (Kolab Systems) <vanmeeuwen@kolabsys.com> - 2.2.4-4
- Fix recode_message() boundary handling
- Refresh Junk folder patch

* Wed Jan 29 2014 Jeroen van Meeuwen (Kolab Systems) <vanmeeuwen@kolabsys.com> - 2.2.4-2
- Fix From: header on iPad/iPhone activesync clients not having a
  displayName. Set 'activesync_fix_from'
- Fix Junk folders being omitted for synchronization

* Tue Jan 28 2014 Jeroen van Meeuwen (Kolab Systems) <vanmeeuwen@kolabsys.com> - 2.2.4-1
- New upstream release

* Tue Nov 12 2013 Jeroen van Meeuwen <vanmeeuwen@kolabsys.com> - 2.2.3-2
- Fix a trailing slash issue
- New upstream release
- Fixes:
  2385 - Do not depend on kolab_cache behavior
  2386 - Improve performance by skipping IMAP SEARCH when checking
         mail folder for changes
  ???? - Skip SELECT/DELETE ... WHERE id = NULL queries
  2383 - Enable alarms synchronization by default
  2431 - Fix event attendees synchronization from server to the device

* Mon Nov 11 2013 Jeroen van Meeuwen <vanmeeuwen@kolabsys.com> - 2.2.2-3
- Make sure we use the readily available plugins and libraries

* Fri Oct 18 2013 Jeroen van Meeuwen <vanmeeuwen@kolabsys.com> - 2.2.2-1
- New upstream version in sync with cache refactoring

* Mon Oct 14 2013 Jeroen van Meeuwen <vanmeeuwen@kolabsys.com> - 2.2.1-1
- New upstream version 2.2.1

* Sun Sep  8 2013 Jeroen van Meeuwen <vanmeeuwen@kolabsys.com> - 2.2.0-1
- Release version 2.2.0

* Wed Sep  3 2013 Jeroen van Meeuwen <vanmeeuwen@kolabsys.com> - 2.1.0-1
- Bug fixes for #1658, and attachment sending

* Tue Mar 12 2013 Jeroen van Meeuwen <vanmeeuwen@kolabsys.com> - 2.1-0.2.rc2
- New upstream release

* Tue Feb 12 2013 Jeroen van Meeuwen <vanmeeuwen@kolabsys.com> - 2.1-0.1.rc1
- Check in new release 2.1-rc1

* Sun Dec  9 2012 Jeroen van Meeuwen <vanmeeuwen@kolabsys.com> - 2.0.0-0.2
- Pull in the required configuration

* Tue Nov 27 2012 Jeroen van Meeuwen <vanmeeuwen@kolabsys.com> - 2.0.0-0.1
- New snapshot that fixes SMTP Auth (#1380)

* Thu Sep 27 2012 Jeroen van Meeuwen <vanmeeuwen@kolabsys.com> - 1.0.1-2
- Apply fix for authentication failing

* Fri Sep 21 2012 Jeroen van Meeuwen <vanmeeuwen@kolabsys.com> - 1.0.1-1
- New upstream release

* Wed Sep 19 2012 Jeroen van Meeuwen <vanmeeuwen@kolabsys.com> - 1.0-0.1
- On the road to version 1.0, distribute a snapshot

* Wed Aug  1 2012 Jeroen van Meeuwen <vanmeeuwen@kolabsys.com> - 0.1-0.2
- New git master snapshot

* Wed Jul 25 2012 Jeroen van Meeuwen <vanmeeuwen@kolabsys.com> - 0.1-0.1
- This is a package, too
