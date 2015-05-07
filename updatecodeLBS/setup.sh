#!/bin/bash

nightlypkgobs=home:tpokorra:branches:Kolab:Development
yum -y install osc php-cli php-xml php-mbstring php-ldap git || exit -1

cp ~/.ssh/oscrc ~/.oscrc
mkdir ~/.composer
cp ~/.ssh/gitauth ~/.composer/auth.json

eval `ssh-agent`
ssh-add ~/.ssh/gitkey
ssh-keyscan -H github.com >> ~/.ssh/known_hosts
git clone --depth 1 git@github.com:TBits/lbs-kolab-nightly.git || exit -1

mkdir osc
cd osc

TODAY=`date +%Y%m%d`

gitnames=( F/freebusy I/iRony C/chwala P/pykolab WAP/webadmin LK/libkolab LKX/libkolabxml S/syncroton \
           RPK/roundcubemail-plugins-kolab LC/libcalendaring PNL/php-Net_LDAP3 U/utils)

for gitname in "${gitnames[@]}"
do
    pkgname=`basename $gitname`
    if [[ "$pkgname" == "webadmin" ]]; then pkgname="kolab-webadmin"; fi
    if [[ "$pkgname" == "freebusy" ]]; then pkgname="kolab-freebusy"; fi
    if [[ "$pkgname" == "utils" ]]; then pkgname="kolab-utils"; fi
    if [[ "$pkgname" == "syncroton" ]]; then pkgname="kolab-syncroton"; fi
    debpkgname=$pkgname
    tarballname=$pkgname
    if [[ "$pkgname" == "php-Net_LDAP3" ]]; then
      pkgname="php-pear-Net-LDAP3"
      debpkgname="php-net-ldap3"
    fi

    osc -A https://obs.kolabsys.com/ checkout Kolab:Development/$pkgname | tee /tmp/osc.log || exit -1
    osc -A https://obs.kolabsys.com/ checkout $nightlypkgobs/$pkgname | tee /tmp/osc.log || exit -1

    cd Kolab:Development/$pkgname

    tar xzf debian.tar.gz
    rm -Rf debian.tar.gz
    # remove release tarball
    rm -Rf *.tar.gz

    mv debian.changelog debian/changelog
    mv debian.control debian/control
    mv debian.series debian/series
    mv debian.rules debian/rules

    # sometimes new files are added in master, which we have to add in the spec file, eg. roundcubemail-plugins-kolab
    if [ -f ../../../$pkgname.patch ]
    then
      patch -p1 < ../../../$pkgname.patch || exit -1
    fi

    serviceVersion=
    if [ -f "_service" ]
    then
      # eg libcalendaring: <param name="versionprefix">4.9.git</param>
      serviceVersion=`cat _service | grep versionprefix | awk -F '>' '{print $2}' | awk -F '.git' '{print $1}' | awk -F '-' '{print $1}' | awk -F '~' '{print $1}'`
    fi

    # Adjust spec file for nightly builds
    sed -i "s#Release:.*#Release:        99.dev%(date +%%Y%%m%%d)%{?dist}#g" $pkgname.spec
    sed -i "s#^Source:.*#Source:         $tarballname-master.tar.gz#g" $pkgname.spec
    sed -i "s#^Source0:.*#Source0:        $tarballname-master.tar.gz#g" $pkgname.spec
    sed -i "s#%setup -q *-c.*#%setupDONE -q -c $tarballname-master#g" $pkgname.spec
    sed -i "s#%setup -q *-n.*#%setupDONE -q -n $tarballname-master#g" $pkgname.spec
    sed -i "s#%setup -q#%setup -q -n $tarballname-master#g" $pkgname.spec
    sed -i "s#%setupDONE#%setup#g" $pkgname.spec
    sed -i "s#%{name}-%{version}#%{name}-master#g" $pkgname.spec
    sed -i "s/pushd %{name}-%{version}/pushd %{name}-master/g" $pkgname.spec
    sed -i "s/%patch/#%patch/g" $pkgname.spec

    # adjust package version if there is _service with versionprefix
    if [ ! -z $serviceVersion ]
    then
      sed -i "s#Version:.*#Version:        $serviceVersion#g" $pkgname.spec
    fi

    # Adjust Debian package files for nightly builds
    DebianPackageVersion=`cat $debpkgname.dsc | grep "^Version:" | awk -F ' ' '{print $2}' | awk -F '-' '{print $1}' | awk -F '~' '{print $1}'`
    if [ ! -z $serviceVersion ]
    then
      DebianPackageVersion=$serviceVersion
    fi
    #Problem: 4.9.1.git > 4.9.1-99.nightly
    DebianPackageVersion=$DebianPackageVersion~nightly$TODAY
    sed -i "s#^Version:.*#Version: $DebianPackageVersion#g" $debpkgname.dsc

    # need to use lowercase package name in changelog
    echo ${debpkgname,,}" ($DebianPackageVersion) unstable; urgency=low" > debian.changelog.new
    echo "  * nightly build" >> debian.changelog.new
    echo " -- Timotheus Pokorra (TBits.net) <tp@tbits.net>  "`date -R` >> debian.changelog.new
    echo "" >> debian.changelog.new
    cat debian/changelog >> debian.changelog.new
    mv -f debian.changelog.new debian/changelog
    echo "" > debian/series

    # some patches are actually part of the package, not backported from git master. we need to keep them
    if [[ "$pkgname" == "chwala" ]]
    then
      sed -i "s/#%patch1/%patch1/g" $pkgname.spec
      echo "chwala-0.2-suhosin.session.encrypt-php_flag.patch -p1" > debian/series
    fi

    if [[ "$pkgname" == "kolab-freebusy" ]]
    then
      git clone --depth 1 https://git.kolab.org/diffusion/F/freebusy.git kolab-freebusy.git
      git clone --depth 1 https://github.com/roundcube/roundcubemail.git roundcubemail.git
      git clone --depth 1 https://git.kolab.org/diffusion/RPK/roundcubemail-plugins-kolab.git roundcubemail-plugins-kolab.git
      cd kolab-freebusy.git
      ./autogen.sh master || exit -1
      mv kolab-freebusy-master+dep.tar.gz ..
      cd ..
      sed -i "s#^Source0:.*#Source0:         $tarballname-master+dep.tar.gz#g" $pkgname.spec
      rm -Rf *.git
      rm -Rf kolab-freebusy-master
    else
      echo "fetching "$tarballname".tar.gz from git.kolab.org"
      while [ ! -f $tarballname-master.tar.gz ]
      do 
        git clone --depth 1 https://git.kolab.org/diffusion/$gitname.git $tarballname-master
        rm -Rf $tarballname-master/.git
        tar czf $tarballname-master.tar.gz $tarballname-master
        rm -Rf $tarballname-master
      done
      if [ ! -f $tarballname-master.tar.gz ];
      then
        echo cannot find $tarballname-master.tar.gz
        exit -1
      fi
    fi

    # for logging the differences
    osc status
    osc diff | cat
    rm -f _service
    cd ../..

    rm -Rf ../lbs-kolab-nightly/$pkgname/*
    mkdir -p ../lbs-kolab-nightly/$pkgname
    cp -R Kolab:Development/$pkgname ../lbs-kolab-nightly/
    rm -Rf ../lbs-kolab-nightly/$pkgname/.osc

    cd $nightlypkgobs/$pkgname
    osc up
    osc pull
    osc repairwc .
    osc resolved *
    rm -Rf *
    cp -Rf ../../Kolab:Development/$pkgname/* .
    mv debian/changelog debian.changelog
    mv debian/control debian.control
    mv debian/series debian.series
    mv debian/rules debian.rules
    tar czf debian.tar.gz debian
    rm -Rf debian
    sed -i "s#^Name:#%define release_prefix dev%(date +%%Y%%m%%d)\nName:#g" $pkgname.spec
    osc addremove
    osc commit -m "nightly build for $TODAY" || exit -1 
    
    cd ../../
done

cd ../lbs-kolab-nightly
git add .
git config --global user.name "LBS BuildBot"
git config --global user.email tp@tbits.net

git commit -a -m "nightly build for $TODAY" || exit -1

git push || exit -1
