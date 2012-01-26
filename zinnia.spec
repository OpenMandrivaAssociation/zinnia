Summary: 	Online hand recognition system with machine learning
Name: 		zinnia
Version: 	0.06
Release:	3
License: 	BSD
Group: 		System/Internationalization
Source0: 	http://downloads.sourceforge.net/zinnia/%{name}-%version.tar.gz
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
Requires:	%{libname} = %{version}
Requires:	pkgconfig
Provides:	%{name}-devel = %{version}-%{release}

%description -n	%{devname}
This package contains development files for %{name}.

%package -n	perl-%{name}
Summary:	Perl bindings for %{name}
Group:		Development/Perl
Requires:	%{name} = %{version}

%description -n	perl-%{name}
This package contains perl bindings for %{name}.

%package -n	python-%{name}
Summary:	Python bindings for %{name}
Group:		Development/Python
Requires:	%{name} = %{version}
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
%{_bindir}/*

%files -n %{libname}
%{_libdir}/*.so.%{major}*

%files -n %{devname}
%doc doc/*
%{_includedir}/*.h
%{_includedir}/%{name}
%{_libdir}/*.so
%{_libdir}/pkgconfig/%{name}.pc

%files -n perl-%{name}
%{perl_vendorarch}/auto/zinnia/zinnia.so
%{perl_vendorarch}/zinnia.pm

%files -n python-%{name}
%{py_platsitedir}/*
