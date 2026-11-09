--# -path=.:alltenses:prelude
-- FR concrete for development-only six-operation semantic profile.
concrete DefluensCoreFre of DefluensCore = open SyntaxFre, ParadigmsFre in {
  flags coding = utf8 ;
  flags unlexer = text ;
  lincat Output = {s : Str} ; Subject = NP ; Quality = AP ; Kind = N ;
    EventV = V ; ActionV2 = V2 ; ObjectNP = NP ; Place = Adv ; CommandV = V ;
    Polarity = Pol ; TimeRef = Tense ;
  lin
    RealizeAttribute x a p t = {s = (mkUtt (mkS t p (mkCl x a))).s} ;
    RealizeClass x a p t = {s = (mkUtt (mkS t p (mkCl x a))).s} ;
    RealizeEvent x v p t = {s = (mkUtt (mkS t p (mkCl x v))).s} ;
    RealizeAction x v o p t = {s = (mkUtt (mkS t p (mkCl x v o))).s} ;
    RealizeLocation x a p t = {s = (mkUtt (mkS t p (mkCl x a))).s} ;
    RealizeDirective v p = {s = (mkUtt p (mkImp v)).s} ;
    Mira_Subject = mkNP (mkPN "Mira" feminine) ;
    Lea_Subject = mkNP (mkPN "Léa" feminine) ;
    Noa_Subject = mkNP (mkPN "Noa" masculine) ;
    Ready_Quality = mkAP (mkA "prêt" "prête") ;
    Calm_Quality = mkAP (mkA "calme") ;
    Absent_Quality = mkAP (mkA "absent" "absente") ;
    Available_Quality = mkAP (mkA "disponible") ;
    Guide_Kind = mkN "guide" ;
    Artist_Kind = mkN "artiste" ;
    Scientist_Kind = mkN "scientifique" ;
    Work_Event = mkV "travailler" ;
    Walk_Event = mkV "marcher" ;
    Speak_Event = mkV "parler" ;
    Carry_Action = mkV2 (mkV "porter") ;
    Watch_Action = mkV2 (mkV "regarder") ;
    Visit_Action = mkV2 (mkV "visiter") ;
    Book_Object = mkNP (mkN "livre") ;
    Document_Object = mkNP (mkN "document") ;
    Flower_Object = mkNP (mkN "fleur" feminine) ;
    Here_Place = ParadigmsFre.mkAdv "ici" ;
    There_Place = ParadigmsFre.mkAdv "là" ;
    InParis_Place = ParadigmsFre.mkAdv "à Paris" ;
    Wait_Command = mkV "patienter" ;
    Walk_Command = mkV "marcher" ;
    Speak_Command = mkV "parler" ;
    Positive_Polarity = positivePol ;
    Negative_Polarity = negativePol ;
    Present_Time = presentTense ;
    Past_Time = pastTense ;
    Future_Time = futureTense ;
}
