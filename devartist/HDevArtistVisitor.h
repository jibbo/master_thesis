/*
 * Copyright (C) 2014 The Android Open Source Project
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
 */

#ifndef ART_MODULES_DEVARTIST_HDEVARTISTVISITOR_H_
#define ART_MODULES_DEVARTIST_HDEVARTISTVISITOR_H_

#include "optimizing/artist/artist_method_visitor.h"
#include "optimizing/nodes.h"
#include "optimizing/artist/artist_utils.h"
#include "optimizing/artist/verbose_printer.h"
#include "optimizing/artist/env/codelib_environment.h"
#include "optimizing/artist/env/codelib.h"
#include "optimizing/artist/artist.h"


#include "optimizing/artist/injection/short.h"
#include "optimizing/artist/injection/boolean.h"
#include "optimizing/artist/injection/byte.h"
#include "optimizing/artist/injection/char.h"
#include "optimizing/artist/injection/double.h"
#include "optimizing/artist/injection/float.h"
#include "optimizing/artist/injection/integer.h"
#include "optimizing/artist/injection/long.h"
#include "optimizing/artist/env/codelib.h"
#include "optimizing/artist/injection/injection.h"

#include <memory>
#include <string>
#include <algorithm>

namespace art {
    class HDevArtistVisitor : public HArtistMethodVisitor {
    public:
        explicit HDevArtistVisitor(HGraph *graph, const DexCompilationUnit &_dex_compilation_unit, HArtist *artist)
            : HArtistMethodVisitor(graph), _dex(_dex_compilation_unit), _artist(artist) {}

        void VisitInvokeStaticOrDirect(HInvokeStaticOrDirect *instruction) override;

        void VisitInvokeVirtual(HInvokeVirtual *instruction) override;

    private:
        const DexCompilationUnit &_dex;

        HArtist *_artist;

//        bool obfuscationDetected = false;

        void printGraph() const;

        void processRawQuery(HInvoke *instruction) const;

        void processRandom(HInvoke *instruction) const;

        void processInvoke(HInvoke *instruction);

        void SqlCompSearchInputs(HInstruction *instruction, HInvoke *cursor) const;

        void SqlCompSearchUses(HInstruction *instruction, HInvoke *cursor) const;

        void addSqlQueryComponent(HInvoke *cursor, HInstruction *component) const;

        string GetSignatureFromType(Primitive::Type type) const;

        void processMessageDigest(HInvoke *instruction);
    };
}  // namespace art
#endif  // ART_MODULES_DEVARTIST_HDEVARTISTVISITOR_H_
