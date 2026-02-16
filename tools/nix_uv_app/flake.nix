{
  description = "A tiny library for packaging uv projects in Nix";

  outputs = { self }: {
    lib = {
      buildUvApp = { pkgs, pname, version, src, entryPoint, hash ? "" }: 
        let
          # This intermediate derivation fetches dependencies
          deps = pkgs.stdenv.mkDerivation {
            name = "${pname}-deps";
            inherit src;
            nativeBuildInputs = [ pkgs.uv pkgs.python3 ];
            outputHashAlgo = "sha256";
            outputHashMode = "recursive";
            outputHash = hash; # You'll fill this in after the first failed build
    
            buildPhase = ''
              export UV_CACHE_DIR=$TMPDIR/uv-cache
              export UV_NO_MANAGED_PYTHON=1
              export UV_PYTHON=${pkgs.python3}/bin/python3
              uv sync --frozen --no-dev
            '';
    
            installPhase = "cp -r .venv $out";
          };
        in
        pkgs.stdenv.mkDerivation {
          inherit pname version src;
          nativeBuildInputs = [ pkgs.makeWrapper ];
          
          installPhase = ''
            mkdir -p $out/share/${pname} $out/bin
            cp -r . $out/share/${pname}
            # Link the pre-built venv from the FOD
            ln -s ${deps} $out/share/${pname}/.venv
    
            cat <<EOF > $out/share/${pname}/run-wrapper.sh
#!/usr/bin/env bash
exec "$out/share/${pname}/.venv/bin/python3" "$out/share/${pname}/${entryPoint}" "\$@"
EOF
            chmod +x $out/share/${pname}/run-wrapper.sh
            makeWrapper $out/share/${pname}/run-wrapper.sh $out/bin/${pname} \
              --prefix PATH : ${pkgs.lib.makeBinPath [ pkgs.python3 pkgs.bash ]}
          '';
        };
    };
  };
}
