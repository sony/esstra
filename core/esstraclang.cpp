// SPDX-FileCopyrightText: Copyright 2026 ESSTRA Contributors
// SPDX-License-Identifier: MIT

#include "clang/Frontend/FrontendPluginRegistry.h"
#include "clang/AST/ASTConsumer.h"
#include "clang/Frontend/CompilerInstance.h"
#include "clang/Lex/PPCallbacks.h"
#include "clang/Lex/Preprocessor.h"
#include "llvm/Support/raw_ostream.h"

using namespace clang;

namespace {

class EsstraPPCallbacks : public PPCallbacks {
public:
  void InclusionDirective(SourceLocation HashLoc, const Token &IncludeTok,
                          StringRef FileName, bool IsAngled,
                          CharSourceRange FilenameRange, OptionalFileEntryRef File,
                          StringRef SearchPath, StringRef RelativePath,
                          const Module *Imported,
                          SrcMgr::CharacteristicKind FileType) override {
    if (File) {
      // ponytail: PPCallbacks collect included headers for .esstra section
      llvm::errs() << "[ESSTRA Clang] Include: " << File->getName() << "\n";
    }
  }
};

class EsstraASTConsumer : public ASTConsumer {
public:
  EsstraASTConsumer(CompilerInstance &CI) {
    CI.getPreprocessor().addPPCallbacks(std::make_unique<EsstraPPCallbacks>());
  }
};

class EsstraPluginAction : public PluginASTAction {
protected:
  std::unique_ptr<ASTConsumer> CreateASTConsumer(CompilerInstance &CI,
                                                 StringRef) override {
    return std::make_unique<EsstraASTConsumer>(CI);
  }

  bool ParseArgs(const CompilerInstance &CI,
                 const std::vector<std::string> &args) override {
    return true;
  }
};

} // namespace

static FrontendPluginRegistry::Add<EsstraPluginAction>
    X("esstraclang", "ESSTRA LLVM/Clang Plugin for embedding provenance");
