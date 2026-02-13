{ pkgs ? import <nixpkgs> {} }:

pkgs.stdenv.mkDerivation {
  pname = "hello-cpp";
  version = "1.0";

  src = ./.;  # Keep in mind, this is not a good practice

  # These are native for stdenv
  nativeBuildInputs = [ 
    pkgs.gcc 
  ];
  # Nix expects a 'buildPhase' to compile and an 'installPhase' to move the binary
  buildPhase = ''
    g++ main.cpp -o hello-cpp
  '';

  installPhase = ''
    mkdir -p $out/bin
    cp hello-cpp $out/bin/
  '';
}
