%define anolis_release 1

%define name keentune-target
%define version 1.0.0
%define release 1

#
# spec file for package python-keentune-target
#

%{?!python_module:%define python_module() python3-%{**}}
Name:           %{name}
Version:        %{version}
Release:        1.%{anolis_release}%{?dist}

Summary:        Parameters setting, reading and backup models for KeenTune
Source0:        %{name}-%{version}.tar.gz
License:        Apache License
Group:          Development/Languages/Python
BuildArch:      noarch
BuildRequires:  %{python_module setuptools}
Requires:       tornado >= 6.1
Vendor:         Alibaba


%description
Parameters setting, reading and backup models for KeenTune

%prep
%setup -q -n %{name}-%{version}

%build
python3 setup.py build

%install
python3 setup.py bdist_rpm
arch_path=../../RPMS/`arch`
if [ ! -d $arch_path ]; then
        mkdir -p $arch_path
fi

/bin/cp -f ./dist/*.noarch.rpm  $arch_path/

%clean
rm -rf $RPM_BUILD_ROOT

%changelog
* Wed Aug 18 2021 runzhe.wrz <runzhe.wrz@alibaba-inc.com> - 1.0.0-1
- Initial KeenTune-target
