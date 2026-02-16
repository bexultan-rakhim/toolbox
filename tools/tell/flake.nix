{
  description = "AI-powered CLI tool that generates concise summaries from local cli tools using LangChain and Ollama.";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    uv-app = {
      url = "github:bexultan-rakhim/toolbox?dir=tools/nix_uv_app";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    flake-utils = {
      url = "github:numtide/flake-utils";
      inputs.nixpkgs.follows = "nixpkgs";
    }; 
  };

  outputs = { self, nixpkgs, uv-app, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs =  nixpkgs.legacyPackages.${system};
      in 
      {
      packages.default = uv-app.lib.buildUvApp {
        inherit pkgs;
        pname = "tell";
        version = "0.1.0";
        src = ./.;
        entryPoint = "tell.py";
      };
    });
}
