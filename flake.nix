{
  description = "Reproducible documentary timeline research and editing environment";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { nixpkgs, ... }:
    let
      systems = [ "x86_64-linux" "aarch64-linux" ];
      forAllSystems = nixpkgs.lib.genAttrs systems;
    in
    {
      devShells = forAllSystems (system:
        let
          pkgs = import nixpkgs { inherit system; };
          python = pkgs.python3.withPackages (ps: [
            ps.jsonschema
            ps.pyyaml
            ps.scenedetect
          ]);
          corePackages = with pkgs; [
            actionlint
            ffmpeg
            git
            gnumake
            jq
            python
            shellcheck
            whisper-cpp
            yt-dlp
          ];
        in
        {
          default = pkgs.mkShell {
            packages = corePackages;
          };

          visual = pkgs.mkShell {
            packages = corePackages ++ (with pkgs; [
              chromium
              imagemagick
              nodejs_22
              uv
            ]);
            DOCUMENTARY_CHROMIUM = "${pkgs.chromium}/bin/chromium";
          };
        });
    };
}
