Summary: 	Online hand recognition system with machine learning
Name: 		zinnia
Version: 	0.07
Release:11
License: 	BSD
Group: 		System/Internationalization
Source0: 	https://github.com/silverhikari/zinnia/releases/download/%{version}/zinnia-%{version}.tar.gz
#Source0: http://downloads.sourceforge.net/zinnia/zinnia-0.07.tar.gz
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

%if 0
%package -n	python-%{name}
Summary:	Python bindings for %{name}
Group:		Development/Python
Requires:	%{name} = %{EVRD}
Provides:	tegaki-engine

%description -n	python-%{name}
This package contains python bindings for %{name}.
%endif

%prep
%autosetup -p1

%build
# fix build on aarch64
autoreconf -vfi
%configure --disable-static
%make_build

# Stage library so bindings can link before final %install
%make_install DESTDIR=$PWD/_stage
STAGE_LIB=$PWD/_stage%{_libdir}
STAGE_INC=$PWD/_stage%{_includedir}
ls -la .libs "$STAGE_LIB" 2>/dev/null || true
# ensure -lzinnia can resolve (need unversioned .so for linker -l)
for d in .libs "$STAGE_LIB"; do
  [ -d "$d" ] || continue
  (cd "$d" && for f in libzinnia.so.*; do
     [ -e "$f" ] || continue
     ln -sf "$f" libzinnia.so 2>/dev/null || true
   done)
done


# SWIG wraps need zinnia.h
cp -a zinnia.h swig/ perl/ python/ 2>/dev/null || true

pushd swig
make -j1 perl \
	CPPFLAGS="-I.. -I. -I$STAGE_INC" \
	CFLAGS="%{optflags} -I.. -I. -I$STAGE_INC" \
	CXXFLAGS="%{optflags} -I.. -I. -I$STAGE_INC"
popd

pushd perl
# link against staged or in-tree shared library
ZLIB=$(ls -1 ../.libs/libzinnia.so* $STAGE_LIB/libzinnia.so* 2>/dev/null | head -1)
echo "Using zinnia lib: $ZLIB"
%{__perl} Makefile.PL INSTALLDIRS=vendor \
	INC="-I.. -I. -I$STAGE_INC" \
	LIBS="-L../.libs -L$STAGE_LIB -lzinnia"
sed -i \
	-e "s|^LD_RUN_PATH.*|LD_RUN_PATH =|" \
	-e "s|^LDLOADLIBS.*|LDLOADLIBS = -L../.libs -L$STAGE_LIB -lzinnia|" \
	-e "s|^OTHERLDFLAGS.*|OTHERLDFLAGS = -L../.libs -L$STAGE_LIB -Wl,-rpath-link,../.libs -Wl,-rpath-link,$STAGE_LIB -lzinnia|" \
	Makefile
# if still needed, link with explicit .so path
%{__make} OPTIMIZE="%{optflags} -I.. -I." LDLOADLIBS="-L../.libs -L$STAGE_LIB -lzinnia" \
	OTHERLDFLAGS="-L../.libs -L$STAGE_LIB -Wl,-rpath-link,../.libs" || \
	c++ -shared -o blib/arch/auto/zinnia/zinnia.so zinnia_wrap.o -L../.libs -L$STAGE_LIB -lzinnia -lperl -lpthread
popd

# skip python/ruby/java for a reliable perl package rebuild
# (optional bindings can return later)

%install
%make_install

%make_install -C perl

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

%if 0
%files -n python-%{name}
%{py_platsitedir}/_zinnia.*.so
%{py_platsitedir}/zinnia.py*
%{py_platsitedir}/zinnia_python-*info
%endif
