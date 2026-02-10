{ # this is a template!
  description = "My Home Manager Flake";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    home-manager = {
      url = "github:nix-community/home-manager";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { nixpkgs, home-manager, ... }:
    let
      system = "x86_64-linux"; # Use "aarch64-linux" for ARM, "x86_64-darwin" for Intel Mac, or "aarch64-darwin" for Apple Silicon (i.e. M1, M2, M3, M4 chips)
      pkgs = nixpkgs.legacyPackages.${system};
    in {
      homeConfigurations."<your-username>" = home-manager.lib.homeManagerConfiguration { # replace <your-username> with username on your system
        inherit pkgs;
        modules = [ ./home.nix ]; # This points to your home.nix file that you will create in the next step
      };
    };
}

