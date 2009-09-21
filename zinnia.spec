%define major 0
%define libname %mklibname %name %major
%define develname %mklibname -d %name

Summary: 	Online hand recognition system with machine learning
Name: 		zinnia
Version: 	0.02
Release: 	%mkrel 3
License: 	BSD
Group: 		System/Internationalization
Source: 	http://downloads.sourceforge.net/zinnia/%name-%version.tar.gz
Patch0:		zinnia-0.02-bindings.patch
Patch1:		zinnia-0.02-fix-str-fmt.patch
URL: 		http://zinnia.sourceforge.net/
Buildroot: 	%{_tmppath}/%{name}-%{version}-buildroot
BuildRequires:	perl-devel python-devel
Suggests: 	zinnia-tomoe

%description
Zinnia is a simple, customizable and portable online hand recognition
system based on Support Vector Machines. Zinnia simply receives user
pen strokes as a sequence of coordinate data and outputs n-best
characters sorted by SVM confidence. To keep portability, Zinnia
doesn't have any rendering functionality. In addition to recognition,
Zinnia provides training module that allows us to create any hand-
written recognition systems with low-cost.

%package -n %libname
Summary:	Libraries for %name
Group:		System/Internationalization

%description -n %libname
This package contains shared libraries for %name.

%package -n %develname
Summary:	Development files for %name
Group:		System/Internationalization
Requires:	%libname = %version
Provides:	%name-devel = %version-%release

%description -n %develname
This package contains development files for %name.

%package -n perl-%name
Summary:	Perl bindings for %name
Group:		Development/Perl

%description -n perl-%name
This package contains perl bindings for %name.

%package -n python-%name
Summary:	Python bindings for %name
Group:		Development/Python

%description -n python-%name
This package contains python bindings for %name.

%prep
%setup -q -n %{name}-%{version}
%patch0 -p0
%patch1 -p0

%build
%configure2_5x --disable-static
%make

pushd perl
%{__perl} Makefile.PL INSTALLDIRS=vendor
%{__make} OPTIMIZE="%{optflags}"
popd

pushd python
CFLAGS="%{optflags} -I../" LDFLAGS="-L../.libs" python setup.py build
popd

%install
rm -rf %{buildroot}
%makeinstall_std

pushd perl
%makeinstall_std
popd

pushd python
python setup.py install --root=%{buildroot}
popd

%clean
rm -rf %{buildroot}

%files
%defattr (-,root,root)
%{_bindir}/*

%files -n %libname
%defattr (-,root,root)
%{_libdir}/*.so.%{major}*

%files -n %develname
%defattr (-,root,root)
%doc doc/*
%{_includedir}/*.h
%{_libdir}/*.so
%{_libdir}/*.la

%files -n perl-%name
%defattr (-,root,root)
%perl_vendorarch/auto/zinnia/zinnia.so
%perl_vendorarch/zinnia.pm

%files -n python-%name
%defattr (-,root,root)
%py_platsitedir/*
