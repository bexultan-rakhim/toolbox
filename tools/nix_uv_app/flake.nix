{
  description = "A tiny library for packaging uv projects in Nix";

  outputs = { self }: {
    lib = {
      buildUvApp = { pkgs, pname, version, src, entryPoint }: 
        pkgs.stdenv.mkDerivation {
          inherit pname version src;

          nativeBuildInputs = [ pkgs.uv pkgs.python3 pkgs.makeWrapper ];

          buildPhase = ''
            export UV_CACHE_DIR=$TMPDIR/uv-cache
            # Ensure a clean sync without dev dependencies
            uv sync --frozen --no-dev
          '';

          installPhase = ''
          mkdir -p $out/share/${pname} $out/bin
            cp -r . $out/share/${pname}
            cat <<EOF > $out/bin/${pname}
            #!/usr/bin/env bash
            VENV_PATH="$out/share/${pname}/.venv"
            PYTHON_SCRIPT="$out/share/${pname}/${entryPoint}"
            
            exec "\$VENV_PATH/bin/python3" "\$PYTHON_SCRIPT" "\$@"
            EOF

            chmod +x $out/bin/${pname}
            
            # Use makeWrapper only to ensure the shell and python are available
            wrapProgram $out/bin/${pname} \
              --prefix PATH : ${pkgs.lib.makeBinPath [ pkgs.python3 pkgs.bash ]}
          '';
        };
    };
  };
}
