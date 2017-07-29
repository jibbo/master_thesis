/**
 * The ARTist Project (https://artist.cispa.saarland)
 *
 * Copyright (C) 2017 CISPA (https://cispa.saarland), Saarland University
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 * @author "Giovanni De Francesco <s8gidefr@stud.uni-saarland.de>"
 *
 */

#include <atomic>

#include "HDevArtist.h"
#include "optimizing/artist/artist_log.h"
#include "optimizing/artist/injection/injection_visitor.h"
#include "optimizing/artist/env/java_env.h"
#include "optimizing/artist/env/codelib.h"
#include "class_linker.h"
#include "class_linker-inl.h"

#include "optimizing/artist/injection/primitives.h"
#include "optimizing/artist/injection/boolean.h"
#include "optimizing/artist/injection/integer.h"
#include "optimizing/artist/injection/float.h"

#include "optimizing/artist/verbose_printer.h"

using std::string;
using std::vector;
using std::shared_ptr;
using std::endl;
using std::sort;

namespace art {

void HDevArtist::SetupModule() {
  VLOG(artistd) << "HDevArtist::SetupModule()";
  // Locked by Environment
//  const std::string& dex_name = ArtUtils::GetDexFileName(graph_);
//  SetupEnvironment(dex_name);

  VLOG(artistd) << "HDevArtist::SetupModule() DONE";
}


void HDevArtist::SetupEnvironment(const std::string& dex_name) {
    VLOG(artistd) << "HDevArtist::SetupEnvironment()";
    CodeLibEnvironment& codeLib = CodeLibEnvironment::GetInstance();
    const std::vector<const DexFile*> dex_files;
    codeLib.SetupEnvironment(dex_files, dex_name, graph_->GetDexFile(), nullptr, nullptr);
    VLOG(artistd) << "HDevArtist::SetupEnvironment() DONE";
    VLOG(artistd) << std::endl;
    VLOG(artistd) << std::endl;
}

void HDevArtist::RunModule()  {
  VLOG(artistd) << "RunTaskDevArtist()";
  CHECK(graph_ != nullptr);
  HDevArtistVisitor visitor(graph_, GetDexCompilationUnit(), this);
  visitor.VisitInsertionOrder();
  VLOG(artistd) << "RunTaskDevArtist() DONE";
}

void HDevArtist::printGraph(const std::string& message) const {
  VLOG(artist) << message;
//  VerbosePrinter verbosePrinter(graph_, dex_compilation_unit);
//  verbosePrinter.VisitReversePostOrder();
//  VLOG(artist) << verbosePrinter.str();
  VLOG(artist) << message << " DONE";
}

}  // namespace art
