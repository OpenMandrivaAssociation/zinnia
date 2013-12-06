Summary: 	Online hand recognition system with machine learning
Name: 		zinnia
Version: 	0.06
Release:	7
License: 	BSD
Group: 		System/Internationalization
Source0: 	http://downloads.sourceforge.net/zinnia/%{name}-%{version}.tar.gz
Patch0:		zinnia-0.05-bindings.patch
URL: 		http://zinnia.sourceforge.net/
BuildRequires:	perl-devel python-devel

%description
Zinnia is a simple, customizable and portable online hand recognition
system based on Support Vector Machines. Zinnia simply receives user
pen strokes as a sequence of coordinate data and outputs n-best
characters sorted by SVM confidence. To keep portability, Zinnia
doesn't have any rendering functionality. In addition to recognition,
Zinnia provides training module that allows us to create any hand-
written recognition systems with low-cost.

%define	major 0
%define	libname	%mklibname %{name} %{major}
%define	devname	%mklibname -d %{name}

%package -n	%{libname}
Summary:	Libraries for %{name}
Group:		System/Internationalization

%description -n	%{libname}
This package contains shared libraries for %{name}.

%package -n	%{devname}
Summary:	Development files for %{name}
Group:		System/Internationalization
Requires:	%{libname} = %{EVRD}
Provides:	%{name}-devel = %{EVRD}

%description -n	%{devname}
This package contains development files for %{name}.

%package -n	perl-%{name}
Summary:	Perl bindings for %{name}
Group:		Development/Perl
Requires:	%{name} = %{EVRD}

%description -n	perl-%{name}
This package contains perl bindings for %{name}.

%package -n	python-%{name}
Summary:	Python bindings for %{name}
Group:		Development/Python
Requires:	%{name} = %{EVRD}
Provides:	tegaki-engine

%description -n	python-%{name}
This package contains python bindings for %{name}.

%prep
%setup -q
%patch0 -p1 -b .bindings~

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
%makeinstall_std

%makeinstall_std -C perl

pushd python
python setup.py install --root=%{buildroot}
popd

%files
%{_bindir}/zinnia*

%files -n %{libname}
%{_libdir}/libzinnia.so.%{major}*

%files -n %{devname}
%doc doc/*
%{_includedir}/zinnia.h
%dir %{_includedir}/%{name}
%{_includedir}/%{name}/zinnia.h
%{_libdir}/libzinnia.so
%{_libdir}/pkgconfig/%{name}.pc

%files -n perl-%{name}
%dir %{perl_vendorarch}/auto/zinnia
%{perl_vendorarch}/auto/zinnia/zinnia.so
%{perl_vendorarch}/zinnia.pm

%files -n python-%{name}
%{py_platsitedir}/_zinnia.so
%{py_platsitedir}/zinnia.py
%{py_platsitedir}/zinnia_python-*-py%{py_ver}.egg-info


%changelog
* Thu Jan 26 2012 Per Øyvind Karlsen <peroyvind@mandriva.org> 0.06-4
+ Revision: 769065
- be more explicit in %%files manifest
- use %%{EVRD} macro
- drop redundant pkgconfig dependency
- cleanups
- drop libtool .la files that's now removed by spec-helper
- svn commit -m mass rebuild of perl extension against perl 5.14.2

* Sat May 14 2011 Funda Wang <fwang@mandriva.org> 0.06-2
+ Revision: 674597
- rebuild

* Tue Nov 02 2010 Funda Wang <fwang@mandriva.org> 0.06-1mdv2011.0
+ Revision: 592289
- add requires
- new version 0.06

* Thu Jul 22 2010 Jérôme Quelin <jquelin@mandriva.org> 0.05-2mdv2011.0
+ Revision: 556784
- perl 5.12 rebuild

* Thu Nov 19 2009 Jérôme Brenier <incubusss@mandriva.org> 0.05-1mdv2010.1
+ Revision: 467434
- new version 0.05
- rediff P0
- drop P1 (no more needed)
- requires : pkgconfig for the devel subpackage
- fix files section

* Mon Sep 21 2009 Thierry Vignaud <tv@mandriva.org> 0.02-3mdv2010.0
+ Revision: 446318
- rebuild

* Sun Feb 15 2009 Funda Wang <fwang@mandriva.org> 0.02-2mdv2009.1
+ Revision: 340609
- bump rel
- add bindings build

* Sun Feb 15 2009 Funda Wang <fwang@mandriva.org> 0.02-1mdv2009.1
+ Revision: 340500
- import zinnia


