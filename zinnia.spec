Summary: 	Online hand recognition system with machine learning
Name: 		zinnia
Version: 	0.07
Release:8
License: 	BSD
Group: 		System/Internationalization
Source0: 	https://github.com/silverhikari/zinnia/releases/download/%{version}/zinnia-%{version}.tar.gz
#Source0: 	http://downloads.sourceforge.net/zinnia/%{name}-%{version}.tar.gz
Patch0:		zinnia-0.05-bindings.patch
# Fix compile on clang.
#Patch1:   fix-compile-std-make-pair.patch
URL: 		https://zinnia.sourceforge.net/
BuildRequires:	libtool-base
BuildRequires:  automake
BuildRequires:  autoconf
BuildRequires:  libtool
BuildRequires:  slibtool
BuildRequires:  m4
BuildRequires:  make
BuildRequires:	swig
BuildRequires:	perl-devel
BuildRequires:	pkgconfig(python3)
BuildRequires:  python%{pyver}dist(setuptools)
BuildRequires:  python%{pyver}dist(pip)

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
%autosetup -p1

%build
# fix build on aarch64
autoreconf -vfi
%configure --disable-static
%make_build

# SWIG/perl/python wraps #include "zinnia.h" — header is in source root
cp -a zinnia.h swig/ 2>/dev/null || true
cp -a zinnia.h perl/ 2>/dev/null || true
cp -a zinnia.h python/ 2>/dev/null || true

pushd swig
make -j1 perl python ruby java \
	CPPFLAGS="-I.. -I." \
	CFLAGS="%{optflags} -I.. -I." \
	CXXFLAGS="%{optflags} -I.. -I."
popd

pushd perl
%{__perl} Makefile.PL INSTALLDIRS=vendor INC="-I.. -I."
%{__make} OPTIMIZE="%{optflags} -I.. -I."
popd

pushd python
CFLAGS="%{optflags} -I.. -I." LDFLAGS="-L../.libs" python setup.py build
popd

%install
%make_install

%make_install -C perl

pushd python
python setup.py install --root=%{buildroot}
popd

find %{buildroot} -name "*.pyc" -exec rm -f {} \;

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
%{py_platsitedir}/_zinnia.*.so
%{py_platsitedir}/zinnia.py*
%{py_platsitedir}/zinnia_python-*info
