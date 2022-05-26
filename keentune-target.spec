%define anolis_release 6

#
# spec file for package KeenTune-target
#

Name:           keentune-target
Version:        1.0.0
Release:        %{?anolis_release}%{?dist}
Url:            https://gitee.com/anolis/keentune_target
Summary:        Parameters setting, reading and backup models for KeenTune
License:        MulanPSLv2
Group:          Development/Languages/Python
Source:         %{name}-%{version}.tar.gz

BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildArch:      noarch

Vendor:         Alibaba

%description
Parameters setting, reading and backup models for KeenTune

%prep
%setup -q -n %{name}-%{version}

%build
%{__python3} setup.py build

%install
%{__python3} setup.py install --single-version-externally-managed -O1 --prefix=%{_prefix} --root=%{buildroot} --record=INSTALLED_FILES
mkdir -p ${RPM_BUILD_ROOT}/usr/lib/systemd/system/
cp -f ./keentune-target.service ${RPM_BUILD_ROOT}/usr/lib/systemd/system/
install -D -m644 man/keentune-target.8 ${RPM_BUILD_ROOT}%{_mandir}/man8/keentune-target.8
install -D -m644 man/keentune-target.conf.5 ${RPM_BUILD_ROOT}%{_mandir}/man5/keentune-target.conf.5
install -D -m644 man/keentune-target.domain.7 ${RPM_BUILD_ROOT}%{_mandir}/man7/keentune-target.domain.7

%clean
rm -rf $RPM_BUILD_ROOT

%postun
SCRIPT_DIR=%{_sysconfdir}/keentune/script
CONF_DIR=%{_sysconfdir}/keentune/conf
rm -rf $SCRIPT_DIR
if [ "$(ls -A $CONF_DIR)" = "" ]; then
        rm -rf $CONF_DIR
fi

%files -f INSTALLED_FILES
%defattr(-,root,root)
%license LICENSE
%{_prefix}/lib/systemd/system/keentune-target.service
%{_mandir}/man8/keentune-target.8*
%{_mandir}/man5/keentune-target.conf.5*
%{_mandir}/man5/keentune-target.domain.7*

%changelog
* Wed Jan 26 2022 lilinjie <lilinjie@uniontech.com> - 1.0.0-6
- remove empty conf/script dir when uninstall keentune-target

* Wed Dec 12 2021 Runzhe Wang <15501019889@126.com> - 1.0.0-5
- fix bug: can not running in alinux2 and centos7
- change modify codeup address to gitee

* Wed Dec 01 2021 Runzhe Wang <15501019889@126.com> - 1.0.0-4
- add keentune to systemd

* Wed Nov 24 2021 Runzhe Wang <15501019889@126.com> - 1.0.0-3
- fix: wrong license in setup.py
- add nginx conf parameter domain

* Wed Nov 10 2021 Runzhe Wang <15501019889@126.com> - 1.0.0-2
- use '%license' macro
- update license to MulanPSLv2

* Wed Aug 18 2021 Runzhe Wang <15501019889@126.com> - 1.0.0-1
- Initial KeenTune-target
