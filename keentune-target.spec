%define anolis_release 1

#
# spec file for package KeenTune-target
#

Name:           keentune-target
Version:        1.1.2
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

%changelog
* Mon May 09 2022 Runzhe Wang <15501019889@126.com> - 1.1.2
- update .service file

* Fri May 06 2022 Runzhe Wang <15501019889@126.com> - 1.1.1
- Modify code format and style

* Wed Mar 03 2022 Runzhe Wang <15501019889@126.com> - 1.1.0
- Add support for GP (in iTuned) in sensitizing algorithms
- Add support for lasso in sensitizing algorithms
- refactor tornado module: replace await by threadpool
- lazy load domain in keentune-target

* Wed Jan 01 2022 Runzhe Wang <15501019889@126.com> - 1.0.1
- Verify input arguments of command 'param tune'
- Supporting of multiple target tuning
- Fix bug which cause keentune hanging after command 'param stop'
- Add verification of conflicting commands such as 'param dump', 'param delete' when a tuning job is runing.
- Remove version limitation of tornado
- Refactor sysctl domain to improve stability of parameter setting
- Fix some user experience issues

* Wed Dec 12 2021 Runzhe Wang <15501019889@126.com> - 1.0.0
- change modify codeup address to gitee
- add keentune to systemd
- fix: wrong license in setup.py
- add nginx conf parameter domain
- update license to MulanPSLv2