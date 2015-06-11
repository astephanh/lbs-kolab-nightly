Format: 1.0
Source: libkolab
Binary: libkolab0, php-kolab, python-kolab, libkolab-dev
Architecture: any
Version: 0.6.0.nightly20150611
Maintainer: Debian Kolab Maintainers <pkg-kolab-devel@lists.alioth.debian.org>
Uploaders: Jeroen van Meeuwen (Kolab Systems) <vanmeeuwen@kolabsys.com>, Christoph Wickert <wickert@kolabsys.com>, Paul Klos <kolab@klos2day.nl>
Homepage: http://git.kolab.org/libkolab
Standards-Version: 3.9.3
Build-Depends:
	cmake,
	debhelper,
	libboost-dev,
    libboost-program-options-dev,
	libboost-thread-dev,
	libboost-system-dev,
	libcalendaring-dev (>= 4.9.1),
	libcurl4-gnutls-dev,
	libkolabxml-dev (>= 1.0),
	libossp-uuid-dev,
	libqt4-dev,
	libxerces-c-dev,
    php5-cli,
	php5-dev,
	python-dev,
	swig (>= 2.0)
Package-List: 
 libkolab-dev deb libdevel optional
 libkolab0 deb libs optional
 php-kolab deb libs optional
 python-kolab deb python optional
Files: 
 00000000000000000000000000000000 0 libkolab-0.6.tar.gz
 00000000000000000000000000000000 0 debian.tar.gz
