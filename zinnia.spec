# LTO + --no-undefined often breaks this old C++ libtool project
%define _disable_lto 1
%define _disable_ld_no_undefined 1

Summary: 	Online hand recognition system with machine learning
Name: 		zinnia
Version: 	0.07
Release:	18
License: 	BSD
Group: 		System/Internationalization
Source0: 	https://github.com/silverhikari/zinnia/releases/download/%{version}/zinnia-%{version}.tar.gz
Patch0:		zinnia-0.05-bindings.patch
URL: 		https://zinnia.sourceforge.net/
BuildRequires:	slibtool
BuildRequires:  automake
BuildRequires:  autoconf
BuildRequires:  m4
BuildRequires:  make
BuildRequires:	swig
BuildRequires:	perl-devel
BuildRequires:	stdc++-devel

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
Requires:	%{libname} = %{EVRD}

%description -n	perl-%{name}
This package contains perl bindings for %{name}.

%prep
%autosetup -p1

%build
# Prefer slibtool. Skip autoreconf: AC_PROG_LIBTOOL needs GNU libtool m4.
# Upstream ships a working configure script.
export LIBTOOL=slibtool
# Ensure make uses slibtool when it invokes ./libtool
if [ -x /usr/bin/slibtool ]; then
  cat > libtool-wrapper.sh <<'EOS'
#!/bin/sh
exec slibtool "$@"
EOS
  chmod +x libtool-wrapper.sh
  export LIBTOOL="$PWD/libtool-wrapper.sh"
fi
%configure --disable-static
# Point generated libtool at slibtool if it is a config script (slibtoolize style)
if [ -f libtool ] && head -1 libtool | grep -q '^#'; then
  : # config-only, ok with slibtool via LIBTOOL=
elif [ -f libtool ]; then
  # replace binary/script with slibtool wrapper
  cat > libtool <<'EOS'
#!/bin/sh
exec slibtool "$@"
EOS
  chmod +x libtool
fi
%make_build LIBTOOL="${LIBTOOL:-slibtool}"

# Hard requirement: shared library must exist
ls -la .libs
test -f .libs/libzinnia.so.0.0.0 -o -f .libs/libzinnia.so.0 -o -n "$(ls .libs/libzinnia.so.* 2>/dev/null | head -1)"
# ensure -lzinnia works
(cd .libs && for f in libzinnia.so.*; do [ -f "$f" ] && ln -sfn "$f" libzinnia.so && break; done)
test -e .libs/libzinnia.so

# SWIG perl wrap
cp -a zinnia.h swig/ perl/ 2>/dev/null || true
pushd swig
make -j1 perl \
	CPPFLAGS="-I.. -I." \
	CFLAGS="%{optflags} -I.. -I." \
	CXXFLAGS="%{optflags} -I.. -I."
popd

pushd perl
ABS_LIBDIR=$(cd ../.libs && pwd)
export LIBRARY_PATH="$ABS_LIBDIR${LIBRARY_PATH:+:$LIBRARY_PATH}"
export LD_LIBRARY_PATH="$ABS_LIBDIR${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
%{__perl} Makefile.PL INSTALLDIRS=vendor \
	INC="-I.. -I." \
	LIBS="-L$ABS_LIBDIR -lzinnia"
# force absolute link line
sed -i \
  -e "s|^LDLOADLIBS.*|LDLOADLIBS = -L$ABS_LIBDIR -lzinnia|" \
  -e "s|^OTHERLDFLAGS.*|OTHERLDFLAGS = -L$ABS_LIBDIR -Wl,-rpath-link,$ABS_LIBDIR|" \
  -e "s|^LD_RUN_PATH.*|LD_RUN_PATH =|" \
  Makefile
%{__make} OPTIMIZE="%{optflags} -I.. -I." \
  LDLOADLIBS="-L$ABS_LIBDIR -lzinnia" \
  OTHERLDFLAGS="-L$ABS_LIBDIR -Wl,-rpath-link,$ABS_LIBDIR"
# fallback manual link if make still fails somehow
if [ ! -f blib/arch/auto/zinnia/zinnia.so ]; then
  mkdir -p blib/arch/auto/zinnia
  c++ -shared -o blib/arch/auto/zinnia/zinnia.so \
    $(find . -name 'zinnia_wrap.o' | head -1) \
    -L$ABS_LIBDIR -lzinnia -lperl -lpthread
fi
test -f blib/arch/auto/zinnia/zinnia.so
popd

%install
# Do not run full "make install" (bin install executes zinnia looking for a model).
install -d %{buildroot}%{_libdir} %{buildroot}%{_bindir} %{buildroot}%{_includedir} %{buildroot}%{_includedir}/zinnia %{buildroot}%{_libdir}/pkgconfig

# Copy shared library artifacts produced by slibtool/libtool
ls -la .libs || true
for f in .libs/libzinnia.so* .libs/libzinnia.a; do
  [ -e "$f" ] || continue
  case "$f" in
    *.def*|*.deps*|*.tmp*|*.lai|*.la) continue ;;
  esac
  # only real ELF .so / versioned libs
  case "$f" in
    *.so|*.so.*|*.a) cp -a "$f" %{buildroot}%{_libdir}/ ;;
  esac
done
# also try non-hidden install from make for lib only
make DESTDIR=%{buildroot} install-libLTLIBRARIES INSTALL="install -p" 2>/dev/null || true
# do not ship static lib/libtool archives; debuginfo needs write on .so
rm -f %{buildroot}%{_libdir}/libzinnia.a %{buildroot}%{_libdir}/libzinnia.la
chmod -R u+w %{buildroot} || true

( cd %{buildroot}%{_libdir}
  # prefer real shared object
  if [ ! -e libzinnia.so.0 ] && [ -e libzinnia.so.0.0.0 ]; then
    ln -sfn libzinnia.so.0.0.0 libzinnia.so.0
  fi
  if [ ! -e libzinnia.so ]; then
    real=$(ls -1 libzinnia.so.[0-9]* 2>/dev/null | head -1)
    [ -n "$real" ] && ln -sfn "$real" libzinnia.so
  fi
)
for b in zinnia zinnia_learn zinnia_convert; do
  if [ -x .libs/$b ]; then
    install -m755 .libs/$b %{buildroot}%{_bindir}/$b
  elif [ -x $b ]; then
    # may be wrapper; try .libs first already done
    install -m755 $b %{buildroot}%{_bindir}/$b 2>/dev/null || true
  fi
done
# headers / pc if missing
[ -f %{buildroot}%{_includedir}/zinnia.h ] || install -m644 zinnia.h %{buildroot}%{_includedir}/
install -d %{buildroot}%{_includedir}/zinnia
[ -f %{buildroot}%{_includedir}/zinnia/zinnia.h ] || install -m644 zinnia.h %{buildroot}%{_includedir}/zinnia/
if [ -f zinnia.pc ]; then
  install -d %{buildroot}%{_libdir}/pkgconfig
  install -m644 zinnia.pc %{buildroot}%{_libdir}/pkgconfig/
fi

# perl install
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
