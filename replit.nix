{ pkgs }:
let
  fresh = import (fetchTarball
    "https://github.com/NixOS/nixpkgs/archive/nixpkgs-unstable.tar.gz")
    { config.allowUnfree = true; };
in {
    deps = [
      fresh.claude-code
      pkgs.moreutils
      pkgs.vim
      pkgs.pandoc
      pkgs.texlive.combined.scheme-full
      pkgs.python39Packages.pip
      pkgs.editorconfig-checker
      pkgs.python39Packages.editorconfig
      pkgs.cowsay
      pkgs.bibtex-tidy
    ];
}
