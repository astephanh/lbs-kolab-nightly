%if 0%{?opensuse_bs}
#!BuildIgnore:  systemd
%endif

%{!?python_sitelib: %define python_sitelib %(python -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

%if 0%{?suse_version} || 0%{?fedora} > 17 || 0%{?rhel} > 6
%global with_systemd 1
%{!?_unitdir:   %global _unitdir /usr/lib/systemd/system/}
%else
%global with_systemd 0
%endif

%global kolab_user kolab
%global kolab_user_id 412
%global kolab_group kolab
%global kolab_group_id 412

%global kolabn_user kolab-n
%global kolabn_user_id 413
%global kolabn_group kolab-n
%global kolabn_group_id 413

%global kolabr_user kolab-r
%global kolabr_user_id 414
%global kolabr_group kolab-r
%global kolabr_group_id 414

Summary:            Kolab Groupware Solution
Name:               pykolab
Version:            0.7.14
Release:        99.dev%(date +%%Y%%m%%d)%{?dist}
License:            GPLv3+
Group:              Applications/System
URL:                http://kolab.org/

Source0:        pykolab-master.tar.gz

Patch0001:          0001-Add-a-function-to-retrieve-the-naming-context-used-f.patch
Patch0002:          0002-Proxy-the-new-naming-context-function.patch
Patch0003:          0003-Use-the-new-domain-naming-context-comparison-functio.patch

BuildRoot:          %{_tmppath}/%{name}-master-%{release}-root
BuildArch:          noarch
%if 0%{?suse_version}
BuildRequires:      autoconf
BuildRequires:      automake
BuildRequires:      fdupes
%endif
BuildRequires:      gcc
BuildRequires:      gettext
BuildRequires:      glib2-devel
BuildRequires:      intltool
BuildRequires:      python
BuildRequires:      python-icalendar
BuildRequires:      python-kolab
BuildRequires:      python-kolabformat
BuildRequires:      python-ldap
BuildRequires:      python-nose
BuildRequires:      python-pyasn1
BuildRequires:      python-pyasn1-modules
BuildRequires:      python-sqlalchemy
%if 0%{?suse_version}
BuildRequires:      python-pytz
%else
BuildRequires:      pytz
%endif
BuildRequires:      python-twisted-core
Requires:           kolab-cli = %{version}-%{release}
Requires:           python-ldap >= 2.4
Requires:           python-pyasn1
Requires:           python-pyasn1-modules
Requires(pre):      /usr/sbin/useradd
Requires(pre):      /usr/sbin/usermod
Requires(pre):      /usr/sbin/groupadd

%if 0%{?with_systemd}
%if 0%{?suse_version}
Requires(post):     systemd
Requires(postun):   systemd
Requires(preun):    systemd
%else
%if 0%{?opensuse_bs} == 0
Requires(post):     systemd-units
Requires(postun):   systemd-units
Requires(preun):    coreutils
Requires(preun):    systemd-units
%endif
%endif
%else
Requires(post):     chkconfig
Requires(post):     initscripts
Requires(postun):   initscripts
Requires(preun):    chkconfig
Requires(preun):    initscripts
%endif

%description
Kolab enables you to easily build a groupware server as part of a
collaborative environment.

##
## Kolab Telemetry Logging
##
%package telemetry
Summary:            Kolab Telemetry Logging Capabilities
Group:              Applications/System
Requires:           kolab-cli = %{version}-%{release}

%description telemetry
Cyrus IMAP Telemetry logging handling capabilities for Kolab Groupware

##
## Kolab XML
##
%package xml
Summary:            Kolab XML format wrapper for %{name}
Group:              Applications/System
Requires:           %{name} = %{version}-%{release}
Requires:           python-icalendar
Requires:           python-kolab
Requires:           python-kolabformat >= 0.5

%description xml
Kolab Format XML bindings wrapper for %{name}

##
## Kolab CLI
##
%package -n kolab-cli
Summary:            Kolab CLI components
Group:              Applications/System
Requires:           %{name} = %{version}-%{release}
Requires:           python-augeas
Requires:           python-cheetah
Requires:           python-sqlalchemy

%description -n kolab-cli
Kolab CLI utilities

##
## Kolab SASL Authentication Daemon
##
%package -n kolab-saslauthd
Summary:            Kolab SASL Authentication Daemon
Group:              Applications/System
Requires:           %{name} = %{version}-%{release}
Requires:           cyrus-sasl
Requires:           cyrus-sasl-plain
Requires:           python-sqlalchemy

%description -n kolab-saslauthd
Kolab SASL Authentication Daemon for multi-domain, multi-authn database deployments

##
## Kolab Server implemented in Python
##
%package -n kolab-server
Summary:            Kolab Server implemented in Python
Group:              Applications/System
Requires:           %{name} = %{version}-%{release}

%description -n kolab-server
Kolab Server implemented in Python

##
## Kolab SMTP Access Policy for Postfix
##
%package -n postfix-kolab
Summary:            Kolab SMTP Access Policy for Postfix
Group:              Applications/System
%if 0%{?suse_version}
BuildRequires:      postfix
%endif
Requires:           postfix
Requires:           %{name} = %{version}-%{release}
Requires:           python-sqlalchemy
%if 0%{?suse_version}
Requires:           python-mysql
%else
Requires:           MySQL-python
%endif

%description -n postfix-kolab
Kolab SMTP Access Policy for Postfix

##
## Wallace
##
%package -n wallace
Summary:            Kolab Content-Filter
Group:              Applications/System
Requires:           %{name} = %{version}-%{release}
Requires:           python-sqlalchemy
%if 0%{?suse_version}
Requires:           python-mysql
%else
Requires:           MySQL-python
%endif
Requires:           python-icalendar >= 3.0
Requires:           %{name}-xml = %{version}-%{release}

%description -n wallace
This is the Kolab Content Filter, with plugins

%prep
%setup -q -n pykolab-master

#%patch0003 -p1 -R
#%patch0002 -p1 -R
#%patch0001 -p1 -R

%build
autoreconf -v || automake --add-missing && autoreconf -v
%configure

%install
rm -rf %{buildroot}
make install DESTDIR=%{buildroot}

%if 0%{?with_systemd}
mkdir -p %{buildroot}/%{_unitdir}
%{__install} -p -m 644 kolabd/kolabd.systemd %{buildroot}/%{_unitdir}/kolabd.service
%{__install} -p -m 644 saslauthd/kolab-saslauthd.systemd %{buildroot}/%{_unitdir}/kolab-saslauthd.service
%{__install} -p -m 644 wallace/wallace.systemd %{buildroot}/%{_unitdir}/wallace.service
mkdir -p %{buildroot}/%{_prefix}/lib/tmpfiles.d/
%{__install} -p -m 644 kolabd/kolabd.tmpfiles.d.conf %{buildroot}/%{_prefix}/lib/tmpfiles.d/kolabd.conf
%{__install} -p -m 644 wallace/wallace.tmpfiles.d.conf %{buildroot}/%{_prefix}/lib/tmpfiles.d/wallace.conf
mkdir -p %{buildroot}/run
%{__install} -d -m 755 %{buildroot}/run/kolabd
%{__install} -d -m 755 %{buildroot}/run/wallaced
%else
mkdir -p %{buildroot}/%{_initddir}
%{__install} -p -m 755 kolabd/kolabd.sysvinit %{buildroot}/%{_initrddir}/kolabd
%{__install} -p -m 755 saslauthd/kolab-saslauthd.sysvinit %{buildroot}/%{_initrddir}/kolab-saslauthd
%{__install} -p -m 755 wallace/wallace.sysvinit %{buildroot}/%{_initrddir}/wallace
%endif

%if 0%{?suse_version}
mkdir -p %{buildroot}/%{_var}/adm/fillup-templates/
%{__install} -p -m 644 kolabd/kolabd.sysconfig %{buildroot}/%{_var}/adm/fillup-templates/sysconfig.kolabd
%{__install} -p -m 644 saslauthd/kolab-saslauthd.sysconfig %{buildroot}/%{_var}/adm/fillup-templates/sysconfig.kolab-saslauthd
%{__install} -p -m 644 wallace/wallace.sysconfig %{buildroot}/%{_var}/adm/fillup-templates/sysconfig.wallace
%else
mkdir -p %{buildroot}/%{_sysconfdir}/sysconfig
%{__install} -p -m 644 kolabd/kolabd.sysconfig %{buildroot}/%{_sysconfdir}/sysconfig/kolabd
%{__install} -p -m 644 saslauthd/kolab-saslauthd.sysconfig %{buildroot}/%{_sysconfdir}/sysconfig/kolab-saslauthd
%{__install} -p -m 644 wallace/wallace.sysconfig %{buildroot}/%{_sysconfdir}/sysconfig/wallace
%endif

%find_lang pykolab

%if 0%{?suse_version}
%fdupes %{buildroot}/%{python_sitelib}
%endif

%pre
# Add the kolab user and group accounts
getent group %{kolab_group} &>/dev/null || groupadd -r %{kolab_group} -g %{kolab_group_id} &>/dev/null
getent passwd %{kolab_user} &>/dev/null || \
    useradd -r -u %{kolab_user_id} -g %{kolab_group} -d %{_localstatedir}/lib/%{kolab_user} -s /sbin/nologin \
        -c "Kolab System Account" %{kolab_user} &>/dev/null || :

gpasswd -a apache kolab >/dev/null 2>&1 || :

getent group %{kolabn_group} &>/dev/null || groupadd -r %{kolabn_group} -g %{kolabn_group_id} &>/dev/null
getent passwd %{kolabn_user} &>/dev/null || \
    useradd -r -u %{kolabn_user_id} -g %{kolabn_group} -d %{_localstatedir}/lib/%{kolabn_user} -s /sbin/nologin \
        -c "Kolab System Account (N)" %{kolabn_user} &>/dev/null || :
    gpasswd -a %{kolabn_user} %{kolab_group} &>/dev/null || :

getent group %{kolabr_group} &>/dev/null || groupadd -r %{kolabr_group} -g %{kolabr_group_id} &>/dev/null
getent passwd %{kolabr_user} &>/dev/null || \
    useradd -r -u %{kolabr_user_id} -g %{kolabr_group} -d %{_localstatedir}/lib/%{kolabr_user} -s /sbin/nologin \
        -c "Kolab System Account (R)" %{kolabr_user} &>/dev/null || :

# Make sure the kolab user and group is added
getent passwd %{cyrus_admin} &>/dev/null || \
    useradd -r -d %{_localstatedir}/lib/%{cyrus_admin} -s /sbin/nologin \
        -c "Kolab Cyrus Administrator Account" %{cyrus_admin} &>/dev/null || :

# Make sure our user has the correct home directory
if [ $1 -gt 1 ] ; then
    usermod -d %{_localstatedir}/lib/%{kolab_user} %{kolab_user} &>/dev/null || :
    usermod -d %{_localstatedir}/lib/%{kolab_user} %{kolabn_user} &>/dev/null || :
    usermod -d %{_localstatedir}/lib/%{kolab_user} %{kolabr_user} &>/dev/null || :
fi

%post -n kolab-saslauthd
%if 0%{?suse_version}
%fillup_and_insserv -in kolab-saslauthd
%endif

if [ "$1" == "1" ]; then
%if 0%{?with_systemd}
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
%else
    /sbin/chkconfig --add kolab-saslauthd
%endif
else
%if 0%{?with_systemd}
    /bin/systemctl condrestart kolab-saslauthd.service >/dev/null 2>&1 || :
%else
    /sbin/service kolab-saslauthd condrestart
%endif
fi

%preun -n kolab-saslauthd
if [ "$1" == "0" ]; then
%if 0%{?with_systemd}
    /bin/systemctl --no-reload disable kolab-saslauthd.service >/dev/null 2>&1 || :
    /bin/systemctl stop kolab-saslauthd.service >/dev/null 2>&1 || :
%else
    /sbin/service kolab-saslauthd stop > /dev/null 2>&1
    /sbin/chkconfig --del kolab-saslauthd
%endif
fi

%post -n kolab-server
%if 0%{?suse_version}
%fillup_and_insserv -in kolabd
%endif

if [ "$1" == "1" ] ; then
%if 0%{?with_systemd}
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
%else
    /sbin/chkconfig --add kolabd
%endif
fi

%preun -n kolab-server
if [ "$1" == "0" ]; then
%if 0%{?with_systemd}
    /bin/systemctl --no-reload disable kolabd.service >/dev/null 2>&1 || :
    /bin/systemctl stop kolabd.service >/dev/null 2>&1 || :
%else
    /sbin/service kolabd stop > /dev/null 2>&1
    /sbin/chkconfig --del kolabd
%endif
fi

%post -n wallace
%if 0%{?suse_version}
%fillup_and_insserv -in wallace
%endif

if [ "$1" == "1" ] ; then
%if 0%{?with_systemd}
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
%else
    chkconfig --add wallace
%endif
else
%if 0%{?with_systemd}
    /bin/systemctl reload-or-try-restart wallace.service >/dev/null 2>&1 || :
%else
    /sbin/service wallace condrestart
%endif
fi

%preun -n wallace
if [ "$1" == "0" ]; then
%if 0%{?with_systemd}
    /bin/systemctl --no-reload disable wallace.service >/dev/null 2>&1 || :
    /bin/systemctl stop wallace.service >/dev/null 2>&1 || :
%else
    /sbin/service wallace stop > /dev/null 2>&1
    /sbin/chkconfig --del wallace
%endif
fi

%check
nosetests -v tests/unit/ ||:

%clean
rm -rf %{buildroot}

%files -f pykolab.lang
%defattr(-,root,root,-)
%doc AUTHORS COPYING README README.tests
%doc conf/kolab.conf
%attr(0750,kolab-n,kolab) %dir %{_sysconfdir}/kolab
%attr(0640,kolab-n,kolab) %config(noreplace) %{_sysconfdir}/kolab/kolab.conf
%dir %{python_sitelib}/pykolab/
%exclude %{python_sitelib}/pykolab/telemetry.*
%{python_sitelib}/pykolab/*.py
%{python_sitelib}/pykolab/*.pyc
%{python_sitelib}/pykolab/*.pyo
%{python_sitelib}/pykolab/auth/
%{python_sitelib}/pykolab/conf/
%{python_sitelib}/pykolab/imap/
%{python_sitelib}/pykolab/itip/
%dir %{python_sitelib}/pykolab/plugins/
%{python_sitelib}/pykolab/plugins/*.py
%{python_sitelib}/pykolab/plugins/*.pyc
%{python_sitelib}/pykolab/plugins/*.pyo
%{python_sitelib}/pykolab/plugins/defaultfolders
%{python_sitelib}/pykolab/plugins/dynamicquota
%{python_sitelib}/pykolab/plugins/recipientpolicy
%exclude %{python_sitelib}/pykolab/plugins/sievemgmt
%if 0%{?suse_version}
%exclude %{python_sitelib}/kolab/
%endif
%{python_sitelib}/cyruslib.py*
%attr(0775,kolab,kolab-n) %dir %{_localstatedir}/lib/kolab/
%attr(0775,kolab,kolab-n) %dir %{_localstatedir}/log/kolab/

%files telemetry
%defattr(-,root,root,-)
%doc AUTHORS COPYING
%{_sbindir}/kolab_parse_telemetry
#%{python_sitelib}/pykolab/cli/commandgroups/telemetry.py
%{python_sitelib}/pykolab/telemetry.*
%{python_sitelib}/pykolab/cli/telemetry/

%files xml
%dir %{python_sitelib}/pykolab/xml
%{python_sitelib}/pykolab/xml/*.py
%{python_sitelib}/pykolab/xml/*.pyc
%{python_sitelib}/pykolab/xml/*.pyo

%files -n kolab-cli
%defattr(-,root,root,-)
%{_sbindir}/kolab
%{_sbindir}/kolab-conf
%{_sbindir}/setup-kolab
%dir %{_sysconfdir}/kolab/templates
%dir %{_datadir}/kolab
%{_datadir}/kolab/templates
%dir %{python_sitelib}/pykolab/cli/
%{python_sitelib}/pykolab/cli/*.py
%{python_sitelib}/pykolab/cli/*.pyc
%{python_sitelib}/pykolab/cli/*.pyo
%exclude %{python_sitelib}/pykolab/cli/sieve
%dir %{python_sitelib}/pykolab/cli/wap
%{python_sitelib}/pykolab/cli/wap/*.py
%{python_sitelib}/pykolab/cli/wap/*.pyc
%{python_sitelib}/pykolab/cli/wap/*.pyo
%dir %{python_sitelib}/pykolab/setup/
%{python_sitelib}/pykolab/setup/*.py
%{python_sitelib}/pykolab/setup/*.pyc
%{python_sitelib}/pykolab/setup/*.pyo
%dir %{python_sitelib}/pykolab/wap_client/
%{python_sitelib}/pykolab/wap_client/*.py
%{python_sitelib}/pykolab/wap_client/*.pyc
%{python_sitelib}/pykolab/wap_client/*.pyo

%files -n kolab-saslauthd
%defattr(-,root,root,-)
%doc AUTHORS COPYING
%if 0%{?with_systemd}
%{_unitdir}/kolab-saslauthd.service
%if 0%{?suse_version}
%dir %{_prefix}/lib/systemd/
%dir %{_prefix}/lib/systemd/system/
%endif
%else
%{_initrddir}/kolab-saslauthd
%endif
%if 0%{?suse_version}
%config(noreplace) %{_var}/adm/fillup-templates/sysconfig.kolab-saslauthd
%else
%config(noreplace) %{_sysconfdir}/sysconfig/kolab-saslauthd
%endif
%{_sbindir}/kolab-saslauthd
%{python_sitelib}/saslauthd/
%if 0%{?suse_version} > 0 || 0%{?fedora} > 17 || 0%{?rhel} > 6
%ghost %dir %{_localstatedir}/run/kolab-saslauthd
%ghost %dir %{_localstatedir}/run/saslauthd
%else
%dir %{_localstatedir}/run/kolab-saslauthd
%dir %{_localstatedir}/run/saslauthd
%endif

%files -n kolab-server
%defattr(-,root,root,-)
%doc AUTHORS COPYING
%if 0%{?with_systemd}
%{_unitdir}/kolabd.service
%if 0%{?suse_version}
%dir %{_prefix}/lib/systemd/
%dir %{_prefix}/lib/systemd/system/
%dir %{_prefix}/lib/tmpfiles.d/
%endif
%{_prefix}/lib/tmpfiles.d/kolabd.conf
%attr(0700,%{kolab_user},%{kolab_group}) %dir /run/kolabd
%else
%{_initrddir}/kolabd
%endif
%if 0%{?suse_version}
%config(noreplace) %{_var}/adm/fillup-templates/sysconfig.kolabd
%else
%config(noreplace) %{_sysconfdir}/sysconfig/kolabd
%endif
%{_sbindir}/kolabd
%{python_sitelib}/kolabd/
%if 0%{?suse_version} > 0 || 0%{?fedora} > 17 || 0%{?rhel} > 6
%ghost %dir %{_localstatedir}/run/kolabd
%else
%attr(0770,kolab,kolab) %dir %{_localstatedir}/run/kolabd
%endif

%files -n postfix-kolab
%defattr(-,root,root,-)
%doc AUTHORS COPYING
%{_libexecdir}/postfix/kolab_smtp_access_policy

%files -n wallace
%defattr(-,root,root,-)
%doc AUTHORS COPYING
%if 0%{?with_systemd}
%{_unitdir}/wallace.service
%if 0%{?suse_version}
%dir %{_prefix}/lib/systemd/
%dir %{_prefix}/lib/systemd/system/
%dir %{_prefix}/lib/tmpfiles.d/
%endif
%{_prefix}/lib/tmpfiles.d/wallace.conf
%attr(0700,%{kolab_user},%{kolab_group}) %dir /run/wallaced
%else
%{_initrddir}/wallace
%endif
%if 0%{?suse_version}
%config(noreplace) %{_var}/adm/fillup-templates/sysconfig.wallace
%else
%config(noreplace) %{_sysconfdir}/sysconfig/wallace
%endif
%{_sbindir}/wallaced
%{python_sitelib}/wallace
%attr(0700,%{kolab_user},%{kolab_group}) %dir %{_var}/spool/pykolab
%attr(0700,%{kolab_user},%{kolab_group}) %dir %{_var}/spool/pykolab/wallace

%changelog
* Thu May 21 2015 Jeroen van Meeuwen <vanmeeuwen@kolabsys.com> - 0.7.14-1
- Release of version 0.7.14 for continuous integration

* Thu May 14 2015 Jeroen van Meeuwen <vanmeeuwen@kolabsys.com> - 0.7.13-1
- Release of version 0.7.13, see;

  https://issues.kolab.org/buglist.cgi?target_milestone=0.7.13&product=pykolab

* Wed May 13 2015 Jeroen van Meeuwen <vanmeeuwen@kolabsys.com> - 0.7.12-1
- Release of version 0.7.12, see;

  https://issues.kolab.org/buglist.cgi?target_milestone=0.7.12&product=pykolab

* Tue Mar 31 2015 Jeroen van Meeuwen <vanmeeuwen@kolabsys.com> - 0.7.11-2
- Back out the changes related to #4459

* Fri Mar 27 2015 Jeroen van Meeuwen <vanmeeuwen@kolabsys.com> - 0.7.11-1
- Release of version 0.7.11, see;

  https://issues.kolab.org/buglist.cgi?target_milestone=0.7.11&product=pykolab

* Wed Feb 25 2015 Jeroen van Meeuwen <vanmeeuwen@kolabsys.com> - 0.7.10-1
- Release of version 0.7.10, see;

  https://issues.kolab.org/buglist.cgi?target_milestone=0.7.10&product=pykolab

* Mon Feb 23 2015 Daniel Hoffend <dh@dotlan.net> - 0.7.9-3
- Default configuration now contains http-auth + trusted local ips

* Mon Feb 23 2015 Daniel Hoffend <dh@dotlan.net> - 0.7.9-2
- set default kolab_freebusy_server to /freebusy

* Mon Feb 23 2015 Timotheus Pokorra (TBits.net) <tp@tbits.net>
- fix for wallace, pid file location, #4673

* Mon Feb 23 2015 Jeroen van Meeuwen (Kolab Systems) <vanmeeuwen@kolabsys.com> - 0.7.9-1
- Release of version 0.7.9, see;

  https://issues.kolab.org/buglist.cgi?target_milestone=0.7.9&product=pykolab

* Fri Feb 20 2015 Timotheus Pokorra (TBits.net) <tp@tbits.net>
- more fixes for CentOS7, fix path for /run/kolabd, fixing #2626
- and fixing path for clamd.sock, #3565

* Thu Feb 19 2015 Timotheus Pokorra (TBits.net) <tp@tbits.net>
- fix for CentOS7, fix path for kolab-saslauthd, fixing #4628

* Wed Feb 18 2015 Daniel Hoffend <dh@dotlan.net> - 0.7.8-3
- deliver to shared folders with spaces #4613

* Sun Feb 15 2015 Daniel Hoffend <dh@dotlan.net> - 0.7.8-2
- plugin threading_as_default no longer exists #4570

* Sat Feb 14 2015 Jeroen van Meeuwen (Kolab Systems) <vanmeeuwen@kolabsys.com> - 0.7.8-1
- Release of version 0.7.8, see;

  https://issues.kolab.org/buglist.cgi?target_milestone=0.7.8&product=pykolab

* Thu Feb 12 2015 Timotheus Pokorra (TBits.net) <tp@tbits.net>
- fix for CentOS7, start service mariadb instead of mysqld. fixing #3877
- use /run/kolabd for the pid, fixing #2626
- fix for CentOS7, only enable dirsrv-admin.service if it actually exists. fixing #4554
- use chameleon skin as default. fixing #4557

* Fri Jan 23 2015 Jeroen van Meeuwen (Kolab Systems) <vanmeeuwen@kolabsys.com> - 0.7.7-1
- Implement #4256, allowing Wallace messages to be localized

* Wed Jan 14 2015 Jeroen van Meeuwen (Kolab Systems) <vanmeeuwen@kolabsys.com> - 0.7.6-1
- Fix LDAP authentication and user searching (#4218)
- Enable error logging for Roundcubemail (#4104)
- Fix comparison of datetime.datetime and datetime.date (#4079)
- Apply invitation policy also to aliases (#4074)

* Wed Dec 31 2014 Jeroen van Meeuwen (Kolab Systems) <vanmeeuwen@kolabsys.com> - 0.7.5-1
- New upstream release
- Fix default configuration for Roundcube plugin managesieve (#4103)
- Fix error due to missing 'domain_name_attribute' variable

* Thu Dec 11 2014 Jeroen van Meeuwen (Kolab Systems) <vanmeeuwen@kolabsys.com> - 0.7.4-5
- Fix #4076 domain filter inconsistency.
- Fix creating additional user folders

* Tue Dec  9 2014 Jeroen van Meeuwen (Kolab Systems) <vanmeeuwen@kolabsys.com> - 0.7.4-3
- Use the correct scheme, hostname and port if so configured
- Set the skin to used based on the available skins

* Mon Dec  8 2014 Jeroen van Meeuwen (Kolab Systems) <vanmeeuwen@kolabsys.com> - 0.7.4-1
- New upstream release

* Fri Oct 31 2014 Jeroen van Meeuwen (Kolab Systems) <vanmeeuwen@kolabsys.com> - 0.7.3-1
- New upstream release

* Mon Sep 15 2014 Daniel Hoffend <dh@dotlan.net> - 0.7.2-2
- added patch to fix setup-kolab mysql.initial
- added patch to fix assets_path

* Thu Sep 11 2014 Jeroen van Meeuwen <vanmeeuwen@kolabsys.com> - 0.7.2-1
- Wrap it all up in a new release

* Tue Aug 26 2014 Aeneas Jaissle <aj@ajaissle.de> - 0.7.1-2
- Added patch to use conf.socketfile in kolab-saslauthd

* Tue Aug 19 2014 Jeroen van Meeuwen (Kolab Systems) <vanmeeuwen@kolabsys.com> - 0.7.1-1
- New upstream release 0.7.1

* Thu Aug 14 2014 Jeroen van Meeuwen (Kolab Systems) <vanmeeuwen@kolabsys.com> - 0.7.0-1
- New upstream release 0.7.0

* Wed Mar  5 2014 Jeroen van Meeuwen (Kolab Systems) <vanmeeuwen@kolabsys.com> - 0.6.13-1
- New upstream release

* Sun Feb 16 2014 Jeroen van Meeuwen (Kolab Systems) <vanmeeuwen@kolabsys.com> - 0.6.12-5
- Close infinite loop

* Sat Feb 15 2014 Jeroen van Meeuwen (Kolab Systems) <vanmeeuwen@kolabsys.com> - 0.6.12-4
- New upstream bug-fix release
- Do not drop privileges too early
- Regenerate auth_cache automatically
- Fix typo in Kolab SMTP Access Policy
- Fix logger switching gid

* Tue Jan 28 2014 Jeroen van Meeuwen (Kolab Systems) <vanmeeuwen@kolabsys.com> - 0.6.11-1
- New upstream release

* Tue Jan 14 2014 Jeroen van Meeuwen (Kolab Systems) <vanmeeuwen@kolabsys.com> - 0.6.10-1
- Fix case-sensitive comparison of server addresses.
- Fix initial synchronization of users with mailhost attributes already set.
- Add configuration option to prevent kolabd from applying the recipient policy.
- Handle errors in subscribing a user to mail folders.

* Fri Jan 10 2014 Jeroen van Meeuwen (Kolab Systems) <vanmeeuwen@kolabsys.com> - 0.6.9-2
- Fix 8bit-passwords not passing through log.debug

* Fri May 17 2013 Jeroen van Meeuwen (Kolab Systems) <vanmeeuwen@kolabsys.com> 0.5.12-2
- Initial package of new upstream version

