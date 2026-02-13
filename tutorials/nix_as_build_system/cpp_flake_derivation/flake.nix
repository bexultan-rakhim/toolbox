{
  description = "A simple C++ Hello World flake";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      # Change this to match your system (e.g., "aarch64-linux" or "x86_64-darwin")
      system = "aarch64-darwin"; 
      pkgs = nixpkgs.legacyPackages.${system};
    in
    {
      packages.${system}.default = pkgs.stdenv.mkDerivation {
        pname = "hello-cpp";
        version = "1.1";
        src = ./.;
        nativeBuildInputs = [ 
          pkgs.gcc 
          pkgs.pkg-config
        ];

        # external dependency!
        buildInputs = [ pkgs.fmt ];

        # Build
        buildPhase = ''
          g++ main.cpp $(pkg-config --cflags --libs fmt) -o hello-cpp
        '';
        
        # Test
        doCheck = true;
        checkPhase = ''
            echo "Running test..."
            ./hello-cpp | grep "Hello"
        
        ''
        
        # Install
        installPhase = ''
          mkdir -p $out/bin
          cp hello-cpp $out/bin/
        '';
      };

     devShells.${system}.default = pkgs.mkShell {
       inputsFrom = [self.packages.${system}.default ];
     };
    };
}

