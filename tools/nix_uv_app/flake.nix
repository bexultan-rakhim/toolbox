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
          
          # 2. Copy the source and .venv
          cp -r . $out/share/${pname}

          # 3. Create the wrapper script directly in the store
          # We use 'install' to set the mode to 755 (executable) immediately
          cat <<EOF > $out/share/${pname}/run-wrapper.sh
#!/usr/bin/env bash
VENV_PATH="$out/share/${pname}/.venv"
PYTHON_SCRIPT="$out/share/${pname}/${entryPoint}"
exec "\$VENV_PATH/bin/python3" "\$PYTHON_SCRIPT" "\$@"
EOF

          # Ensure the wrapper itself is executable
          chmod +x $out/share/${pname}/run-wrapper.sh

          # 4. Use makeWrapper to create the final link in $out/bin
          # This handles the shebang fixup and PATH automatically
          makeWrapper $out/share/${pname}/run-wrapper.sh $out/bin/${pname} \
            --prefix PATH : ${pkgs.lib.makeBinPath [ pkgs.python3 pkgs.bash ]}
          '';
        };
    };
  };
}
