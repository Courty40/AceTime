// This file was generated by the following script:
//
//  $ ../../../tools/process.py --input_dir /home/brian/dev/tz --tz_version 2018h --output_dir /home/brian/dev/AceTime/src/ace_time/zonedb --granularity 900
//
// using the TZ Database files
//
//  africa, antarctica, asia, australasia, europe, northamerica, southamerica
//
// from https://github.com/eggert/tz/releases/tag/2018h
//
// DO NOT EDIT

#ifndef ACE_TIME_ZONE_POLICIES_H
#define ACE_TIME_ZONE_POLICIES_H

#include "../common/ZonePolicy.h"

namespace ace_time {
namespace zonedb {

// numPolicies: 75
extern const common::ZonePolicy kPolicyAN;
extern const common::ZonePolicy kPolicyAQ;
extern const common::ZonePolicy kPolicyAS;
extern const common::ZonePolicy kPolicyAT;
extern const common::ZonePolicy kPolicyAV;
extern const common::ZonePolicy kPolicyAW;
extern const common::ZonePolicy kPolicyArg;
extern const common::ZonePolicy kPolicyArmenia;
extern const common::ZonePolicy kPolicyAus;
extern const common::ZonePolicy kPolicyAzer;
extern const common::ZonePolicy kPolicyBarb;
extern const common::ZonePolicy kPolicyBrazil;
extern const common::ZonePolicy kPolicyCO;
extern const common::ZonePolicy kPolicyCR;
extern const common::ZonePolicy kPolicyCanada;
extern const common::ZonePolicy kPolicyChatham;
extern const common::ZonePolicy kPolicyChile;
extern const common::ZonePolicy kPolicyCook;
extern const common::ZonePolicy kPolicyCuba;
extern const common::ZonePolicy kPolicyDhaka;
extern const common::ZonePolicy kPolicyE_EurAsia;
extern const common::ZonePolicy kPolicyEU;
extern const common::ZonePolicy kPolicyEUAsia;
extern const common::ZonePolicy kPolicyEcuador;
extern const common::ZonePolicy kPolicyEgypt;
extern const common::ZonePolicy kPolicyEire;
extern const common::ZonePolicy kPolicyFalk;
extern const common::ZonePolicy kPolicyFiji;
extern const common::ZonePolicy kPolicyGhana;
extern const common::ZonePolicy kPolicyGuam;
extern const common::ZonePolicy kPolicyGuat;
extern const common::ZonePolicy kPolicyHK;
extern const common::ZonePolicy kPolicyHaiti;
extern const common::ZonePolicy kPolicyHoliday;
extern const common::ZonePolicy kPolicyHond;
extern const common::ZonePolicy kPolicyIran;
extern const common::ZonePolicy kPolicyIraq;
extern const common::ZonePolicy kPolicyJapan;
extern const common::ZonePolicy kPolicyJordan;
extern const common::ZonePolicy kPolicyKyrgyz;
extern const common::ZonePolicy kPolicyLH;
extern const common::ZonePolicy kPolicyLebanon;
extern const common::ZonePolicy kPolicyLibya;
extern const common::ZonePolicy kPolicyMacau;
extern const common::ZonePolicy kPolicyMauritius;
extern const common::ZonePolicy kPolicyMexico;
extern const common::ZonePolicy kPolicyMoldova;
extern const common::ZonePolicy kPolicyMongol;
extern const common::ZonePolicy kPolicyMorocco;
extern const common::ZonePolicy kPolicyNC;
extern const common::ZonePolicy kPolicyNT_YK;
extern const common::ZonePolicy kPolicyNZ;
extern const common::ZonePolicy kPolicyNic;
extern const common::ZonePolicy kPolicyPRC;
extern const common::ZonePolicy kPolicyPakistan;
extern const common::ZonePolicy kPolicyPara;
extern const common::ZonePolicy kPolicyPeru;
extern const common::ZonePolicy kPolicyPhil;
extern const common::ZonePolicy kPolicyROK;
extern const common::ZonePolicy kPolicyRussia;
extern const common::ZonePolicy kPolicyRussiaAsia;
extern const common::ZonePolicy kPolicySA;
extern const common::ZonePolicy kPolicySalv;
extern const common::ZonePolicy kPolicySudan;
extern const common::ZonePolicy kPolicySyria;
extern const common::ZonePolicy kPolicyTaiwan;
extern const common::ZonePolicy kPolicyThule;
extern const common::ZonePolicy kPolicyTonga;
extern const common::ZonePolicy kPolicyTunisia;
extern const common::ZonePolicy kPolicyUS;
extern const common::ZonePolicy kPolicyUruguay;
extern const common::ZonePolicy kPolicyVanuatu;
extern const common::ZonePolicy kPolicyWS;
extern const common::ZonePolicy kPolicyWinn;
extern const common::ZonePolicy kPolicyZion;


// The following zone policies are not supported in the current version of
// AceTime.
//
// numPolicies: 64
//
// kPolicyAlbania (unused)
// kPolicyAlgeria (unused)
// kPolicyAustria (unused)
// kPolicyBahamas (unused)
// kPolicyBelgium (unused)
// kPolicyBelize (LETTER 'CST' too long)
// kPolicyBulg (unused)
// kPolicyC-Eur (unused)
// kPolicyCA (unused)
// kPolicyChicago (unused)
// kPolicyCyprus (unused)
// kPolicyCzech (unused)
// kPolicyDR (unused)
// kPolicyDenmark (unused)
// kPolicyDenver (unused)
// kPolicyDetroit (unused)
// kPolicyE-Eur (unused)
// kPolicyEdm (unused)
// kPolicyEgyptAsia (unused)
// kPolicyFinland (unused)
// kPolicyFrance (unused)
// kPolicyGB-Eire (unused)
// kPolicyGermany (unused)
// kPolicyGreece (unused)
// kPolicyHalifax (unused)
// kPolicyHungary (unused)
// kPolicyIceland (unused)
// kPolicyIndianapolis (unused)
// kPolicyItaly (unused)
// kPolicyLatvia (unused)
// kPolicyLouisville (unused)
// kPolicyLux (unused)
// kPolicyMalta (unused)
// kPolicyMarengo (unused)
// kPolicyMenominee (unused)
// kPolicyMoncton (AT time '0:01' must be multiples of '900' seconds)
// kPolicyNBorneo (unused)
// kPolicyNYC (unused)
// kPolicyNamibia (LETTER 'WAT' too long)
// kPolicyNeth (unused)
// kPolicyNorway (unused)
// kPolicyPalestine (AT time '0:01' must be multiples of '900' seconds)
// kPolicyPerry (unused)
// kPolicyPike (unused)
// kPolicyPoland (unused)
// kPolicyPort (unused)
// kPolicyPulaski (unused)
// kPolicyRegina (unused)
// kPolicyRomania (unused)
// kPolicySanLuis (unused)
// kPolicyShang (unused)
// kPolicySovietZone (unused)
// kPolicySpain (unused)
// kPolicySpainAfrica (unused)
// kPolicyStJohns (AT time '0:01' must be multiples of '900' seconds)
// kPolicyStarke (unused)
// kPolicySwift (unused)
// kPolicySwiss (unused)
// kPolicyToronto (unused)
// kPolicyTroll (LETTER '+02' too long)
// kPolicyTurkey (unused)
// kPolicyVanc (unused)
// kPolicyVincennes (unused)
// kPolicyW-Eur (unused)


}
}

#endif
