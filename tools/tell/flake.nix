{
  description = "A hermetic Python hello world";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem(system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        packages.default = pkgs.writers.writePython3Bin "tell"
        {
            doCheck = false;
            libraries = [ pkgs.python3Packages.langchain pkgs.python3Packages.langchain-ollama ];
        } (builtins.readFile ./tell.py);


        devShells.default = pkgs.mkShell {
          buildInputs = [ 
            (pkgs.python3.withPackages (ps: [ ps.langchain ps.langchain-ollama ])) 
          ];
        };
    });
}
