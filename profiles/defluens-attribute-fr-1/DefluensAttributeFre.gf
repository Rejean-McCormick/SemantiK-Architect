--# -path=.:alltenses:prelude
-- French RGL: agreement, negation, tense and copula come from SyntaxFre.
concrete DefluensAttributeFre of DefluensAttribute =
  open SyntaxFre, ParadigmsFre in {
  flags coding=utf8 ;
  flags unlexer=text ;
  lincat
    Output = {s : Str} ;
    Subject = NP ;
    Quality = AP ;
    Polarity = Pol ;
    TimeRef = Tense ;
  lin
    RealizeAttribute subject quality polarity tense =
      {s = (mkUtt (mkS tense polarity (mkCl subject quality))).s} ;
    Mira_Subject = mkNP (mkPN "Mira" feminine) ;
    Lea_Subject = mkNP (mkPN "Léa" feminine) ;
    Noa_Subject = mkNP (mkPN "Noa" masculine) ;
    Ready_Quality = mkAP (mkA "prêt" "prête") ;
    Calm_Quality = mkAP (mkA "calme") ;
    Absent_Quality = mkAP (mkA "absent" "absente") ;
    Available_Quality = mkAP (mkA "disponible") ;
    Positive_Polarity = positivePol ;
    Negative_Polarity = negativePol ;
    Present_Time = presentTense ;
    Past_Time = pastTense ;
    Future_Time = futureTense ;
}
