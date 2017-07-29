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

#include "HDevArtistVisitor.h"

namespace art {

    void HDevArtistVisitor::VisitInvokeStaticOrDirect(HInvokeStaticOrDirect *instruction) {
      processInvoke(instruction->AsInvoke());
    }

    void HDevArtistVisitor::VisitInvokeVirtual(HInvokeVirtual *instruction) {
      processInvoke(instruction->AsInvoke());
    }

    void HDevArtistVisitor::processInvoke(HInvoke *instruction) {
      string methodName = ArtUtils::GetMethodName(instruction, true);
      VLOG(artist) << "[DC] checking: " << methodName;
      // If you find random and it's not already secureradom.
//      if (methodName.find("java.util.Random.<init>") != std::string::npos) {
//        processRandom(instruction);
//          VLOG(devArtist) << "[DC][RANDOM][UNSAFE]" << methodName;
//      }
//      if (methodName.find("java.security.SecureRandom.<init>") != std::string::npos) {
//          VLOG(devArtist) << "[DC][RANDOM][SAFE]" << methodName;
//      }

//      if (methodName.find("java.security.MessageDigest java.security.MessageDigest.getInstance(java.lang.String)") !=
//          std::string::npos) {
//        processMessageDigest(instruction);
//      }
//
//      if (methodName.find(
//          "android.database.Cursor android.database.sqlite.SQLiteDatabase.rawQuery(java.lang.String, java.lang.String[])") !=
//          std::string::npos) {
//        processRawQuery(instruction);
//      }

//      if (!obfuscationDetected) {
//        transform(methodName.begin(), methodName.end(), methodName.begin(), tolower);
//        if (methodName.find("password") != std::string::npos) {
//          VLOG(devArtist) << "[DC][PASSWORD] Found something with password: " << methodName;
//        }
//      }
//
//      if (!obfuscationDetected) {
//        // proguard starts obfuscating methods names from .a.a that's why this check.
//        if (methodName.find(".a.a") != std::string::npos ||
//            methodName.find(".a.b.") != std::string::npos) {
//          VLOG(devArtist) << "[DC][OBFUSCATED]";
//          obfuscationDetected = true;  // this is just to make this output only once.
//        }
//      }
    }

    void HDevArtistVisitor::processRandom(HInvoke *instruction) const {
      HInstruction *randomInstance = instruction->GetBlock()->GetFirstInstruction();
      do {
        if (randomInstance->IsNewInstance()) {
          VerbosePrinter printer(GetGraph(), _dex);
          printer.VisitNewInstance(randomInstance->AsNewInstance());
          std::string debugMethodName = printer.str();
          if (debugMethodName.find("Ljava/util/Random") != std::string::npos) {
            VLOG(devArtist) << "[DC][RANDOM][FOUND] debugName: " << debugMethodName;
            break;
          }
        }
        randomInstance = randomInstance->GetNext();
      } while (randomInstance != nullptr);


      if (randomInstance != nullptr) {
        printGraph();
        std::vector<HInstruction *> function_params;
        function_params.push_back(_artist->GetCodeLib());
        for (size_t i = 1; i < instruction->InputCount(); i++) {
          function_params.push_back(instruction->InputAt(i));
        }
        std::string signature =
            function_params.size() > 1 ? CodeLib::_M_SAARLAND_CISPA_ARTIST_CODELIB_CODELIB__GETSECURERANDOM_J
                                       : CodeLib::_M_SAARLAND_CISPA_ARTIST_CODELIB_CODELIB__GETSECURERANDOM;

        HInstruction *injection = ArtUtils::InjectMethodCall(instruction,
                                                             signature,
                                                             function_params, Primitive::kPrimNot, true);
        const HUseList<HInstruction *> &useList = randomInstance->GetUses();
        for (auto iterator = useList.begin(), end = useList.end(); iterator != end; iterator++) {
          HInstruction *current = iterator->GetUser();
          for (size_t i = 0; i < current->InputCount(); i++) {
            if (current->InputAt(i)->GetId() == randomInstance->GetId()) {
              current->ReplaceInput(injection, i);
            }
          }
        }
      }
    }


    void HDevArtistVisitor::processRawQuery(HInvoke *instruction) const {
      HInstruction *tmp = instruction->InputAt(1);
      if (tmp->IsLoadString()) {
        // nothing to because it means it contains no parameters.
        VLOG(devArtist) << "[DC][QUERY][SAFE] rawQuery usage: its using a preloaded string";
      } else if (tmp->IsParameterValue()) {
        VLOG(devArtist) << "[DC][QUERY][UNSAFE] rawQuery at instruction:" << instruction->GetId()
                        << ", is using a string as parameter";
        addSqlQueryComponent(instruction, tmp);
        std::vector<HInstruction *> rawQueryParams;
        rawQueryParams.push_back(_artist->GetCodeLib());
        rawQueryParams.push_back(instruction->InputAt(0)->InputAt(0));
        for (size_t i = 1; i < instruction->InputCount(); i++) {
          rawQueryParams.push_back(instruction->InputAt(i));
        }
        ArtUtils::ReplaceMethodCall(instruction,
                                    CodeLib::_M_SAARLAND_CISPA_ARTIST_CODELIB_CODELIB__PATCHEDQUERY,
                                    rawQueryParams, Primitive::kPrimNot);
      } else {
        // we are in a string builder case
        printGraph();
        if (instruction->InputAt(2)->IsNullConstant()) {
          VLOG(devArtist) << "[DC][QUERY][UNSAFE] rawQuery string at: " << instruction->GetId();
          SqlCompSearchInputs(tmp, instruction);
        } else {
          VLOG(devArtist) << "[DC][QUERY][UNCLEAR] rawQuery string at: " << instruction->GetId()
                          << ", is using the selection args";
          // we let the codelib method method scan the selection args.
        }
        std::vector<HInstruction *> rawQueryParams;
        rawQueryParams.push_back(_artist->GetCodeLib());
        rawQueryParams.push_back(instruction->InputAt(0)->InputAt(0));
        for (size_t i = 1; i < instruction->InputCount(); i++) {
          rawQueryParams.push_back(instruction->InputAt(i));
        }
        ArtUtils::ReplaceMethodCall(instruction,
                                    CodeLib::_M_SAARLAND_CISPA_ARTIST_CODELIB_CODELIB__PATCHEDQUERY,
                                    rawQueryParams, Primitive::kPrimNot);
      }
    }

    void HDevArtistVisitor::printGraph() const {
      VerbosePrinter printer(GetGraph(), _dex);
      printer.VisitReversePostOrder();
      VLOG(devArtist) << printer.str();
    }

    static std::vector<HInstruction *> alreadyChecked;

    void HDevArtistVisitor::SqlCompSearchInputs(HInstruction *instruction, HInvoke *cursor) const {
      if (std::find(alreadyChecked.begin(), alreadyChecked.end(), instruction) == alreadyChecked.end()) {
        if (instruction->IsNewInstance()) {
          SqlCompSearchUses(instruction, cursor);
          alreadyChecked.push_back(instruction);
        } else if (instruction->IsLoadString() || instruction->IsConstant()) {
          if (instruction->IsLoadString()) {
            HLoadString *loadString = instruction->AsLoadString();
            VerbosePrinter printer(GetGraph(), _dex);
            printer.VisitLoadString(loadString);
            VLOG(devArtist) << "[DC][QUERY][TRUSTED] rawQuery component: " << printer.str();
          } else {
            addSqlQueryComponent(cursor, instruction);
            alreadyChecked.push_back(instruction);
          }
        } else if (instruction->InputCount() > 0) {
          for (size_t i = 0; i < instruction->InputCount(); i++) {
            alreadyChecked.push_back(instruction);
            SqlCompSearchInputs(instruction->InputAt(i), cursor);
          }
        } else {
          alreadyChecked.push_back(instruction);
        }
      }
    }

    void HDevArtistVisitor::SqlCompSearchUses(HInstruction *instruction, HInvoke *cursor) const {
      if (std::find(alreadyChecked.begin(), alreadyChecked.end(), instruction) == alreadyChecked.end()) {
        VerbosePrinter printer(GetGraph(), _dex);
        printer.VisitInstruction(instruction);
        std::string methodName = printer.str();
        if (instruction->HasUses()) {
          alreadyChecked.push_back(instruction);
          const HUseList<HInstruction *> &useList = instruction->GetUses();
          for (auto iterator = useList.begin(), end = useList.end(); iterator != end; iterator++) {
            SqlCompSearchUses(iterator->GetUser(), cursor);
          }
        } else if (methodName.find("init") == std::string::npos) {
          SqlCompSearchInputs(instruction, cursor);
          alreadyChecked.push_back(instruction);

        } else {
          alreadyChecked.push_back(instruction);
        }
      }
    }

    void HDevArtistVisitor::addSqlQueryComponent(HInvoke *cursor, HInstruction *component) const {
      HInstruction *injection_lib;
      injection_lib = _artist->GetCodeLib();
      std::vector<HInstruction *> function_params;
      function_params.push_back(injection_lib);
      function_params.push_back(component);

      Primitive::Type type = component->GetType();
      std::string signature = GetSignatureFromType(type);

      ArtUtils::InjectMethodCall(cursor,
                                 signature,
                                 function_params,
                                 Primitive::Type::kPrimVoid,
                                 true);
    }

    std::string HDevArtistVisitor::GetSignatureFromType(Primitive::Type type) const {
      if (type == Primitive::Type::kPrimDouble) {
        return CodeLib::_M_SAARLAND_CISPA_ARTIST_CODELIB_CODELIB__ADDSQLCOMPONENT_D_V;
      } else if (type == Primitive::Type::kPrimBoolean) {
        return CodeLib::_M_SAARLAND_CISPA_ARTIST_CODELIB_CODELIB__ADDSQLCOMPONENT_Z_V;
      } else if (type == Primitive::Type::kPrimInt) {
        return CodeLib::_M_SAARLAND_CISPA_ARTIST_CODELIB_CODELIB__ADDSQLCOMPONENT_I_V;
      } else if (type == Primitive::Type::kPrimFloat) {
        return CodeLib::_M_SAARLAND_CISPA_ARTIST_CODELIB_CODELIB__ADDSQLCOMPONENT_F_V;
      } else if (type == Primitive::Type::kPrimChar) {
        return CodeLib::_M_SAARLAND_CISPA_ARTIST_CODELIB_CODELIB__ADDSQLCOMPONENT_C_V;
      } else if (type == Primitive::Type::kPrimLong) {
        return CodeLib::_M_SAARLAND_CISPA_ARTIST_CODELIB_CODELIB__ADDSQLCOMPONENT_J_V;
      } else if (type == Primitive::Type::kPrimShort) {
        return CodeLib::_M_SAARLAND_CISPA_ARTIST_CODELIB_CODELIB__ADDSQLCOMPONENT_S_V;
      } else if (type == Primitive::Type::kPrimByte) {
        return CodeLib::_M_SAARLAND_CISPA_ARTIST_CODELIB_CODELIB__ADDSQLCOMPONENT_B_V;
      } else if (type == Primitive::Type::kPrimNot || type == Primitive::kPrimLast) {
        // TODO ask Oliver
        return CodeLib::_M_SAARLAND_CISPA_ARTIST_CODELIB_CODELIB__ADDSQLCOMPONENT_O_V;
      } else {
        return CodeLib::_M_SAARLAND_CISPA_ARTIST_CODELIB_CODELIB__ADDSQLCOMPONENT_O_V;
      }
    }

    void HDevArtistVisitor::processMessageDigest(HInvoke *instruction) {
      HInstruction *input = instruction->InputAt(0);
      HInstruction *injection_lib = _artist->GetCodeLib();
      std::vector<HInstruction *> function_params;
      function_params.push_back(injection_lib);
      function_params.push_back(input);
      HInstruction *shaInstr = ArtUtils::InjectMethodCall(instruction,
                                                          CodeLib::_M_SAARLAND_CISPA_ARTIST_CODELIB_CODELIB__GETSHAALGORITHMNAME,
                                                          function_params,
                                                          Primitive::Type::kPrimNot,
                                                          true);
      instruction->ReplaceInput(shaInstr, 0);
      VLOG(devArtist) << "[DC][SHA][UNCLEAR]";
    }
}  // namespace art
