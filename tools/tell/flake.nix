{
  description = "AI-powered CLI tool that generates concise summaries from local cli tools using LangChain and Ollama.";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs =  nixpkgs.legacyPackages.${system};
      in 
      {
      packages.default = pkgs.stdenv.mkDerivation {
        pname = "tell";
        version = "0.1.0";
        src = ./.;
        nativeBuildInputs = [pkgs.uv  pkgs.python3 pkgs.makeWrapper ];

        buildPhase = ''
          export UV_CACHE_DIR=$TMPDIR/uv-cache
          uv sync --frozen --no-dev
        '';
        installPhase = ''
           mkdir -p $out/share/tell
           cp -r . $out/share/tell
           makeWrapper  $out/share/tell/tell.sh $out/bin/tell
        '';
     };
    });
}
