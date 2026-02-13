{
  description = "A hermetic Python hello world";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      system = "aarch64-darwin";
      pkgs = nixpkgs.legacyPackages.${system};
    in
    {
      packages.${system}.default = pkgs.writers.writePython3Bin "hello-python"
      {
          libraries = [pkgs.python3Packages.requests];
      } (builtins.readFile ./hello.py);


      devShells.${system}.default = pkgs.mkShell {
        buildInputs = [ 
          (pkgs.python3.withPackages (ps: [ ps.requests ])) 
        ];
      };
    };
}

