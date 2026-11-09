--# -path=.:alltenses:prelude
-- EN concrete for development-only six-operation semantic profile.
concrete DefluensCoreEng of DefluensCore = open SyntaxEng, ParadigmsEng in {
  flags coding = utf8 ;
  flags unlexer = text ;
  lincat Output = {s : Str} ; Subject = NP ; Quality = AP ; Kind = N ;
    EventV = V ; ActionV2 = V2 ; ObjectNP = NP ; Place = Adv ; CommandV = V ;
    Polarity = Pol ; TimeRef = Tense ;
  lin
    RealizeAttribute x a p t = {s = (mkS t p (mkCl x a)).s} ;
    RealizeClass x a p t = {s = (mkS t p (mkCl x a)).s} ;
    RealizeEvent x v p t = {s = (mkS t p (mkCl x v)).s} ;
    RealizeAction x v o p t = {s = (mkS t p (mkCl x v o)).s} ;
    RealizeLocation x a p t = {s = (mkS t p (mkCl x a)).s} ;
    RealizeDirective v p = {s = (mkUtt p (mkImp v)).s} ;
    Mira_Subject = mkNP (mkPN "Mira") ;
    Lea_Subject = mkNP (mkPN "Lea") ;
    Noa_Subject = mkNP (mkPN "Noa") ;
    Ready_Quality = mkAP (mkA "ready") ;
    Calm_Quality = mkAP (mkA "calm") ;
    Absent_Quality = mkAP (mkA "absent") ;
    Available_Quality = mkAP (mkA "available") ;
    Guide_Kind = mkN "guide" ;
    Artist_Kind = mkN "artist" ;
    Scientist_Kind = mkN "scientist" ;
    Work_Event = mkV "work" ;
    Walk_Event = mkV "walk" ;
    Speak_Event = mkV "talk" ;
    Carry_Action = mkV2 (mkV "carry") ;
    Watch_Action = mkV2 (mkV "watch") ;
    Visit_Action = mkV2 (mkV "visit") ;
    Book_Object = mkNP (mkN "book") ;
    Document_Object = mkNP (mkN "document") ;
    Flower_Object = mkNP (mkN "flower") ;
    Here_Place = mkAdv "here" ;
    There_Place = mkAdv "there" ;
    InParis_Place = mkAdv "in Paris" ;
    Wait_Command = mkV "wait" ;
    Walk_Command = mkV "walk" ;
    Speak_Command = mkV "talk" ;
    Positive_Polarity = positivePol ;
    Negative_Polarity = negativePol ;
    Present_Time = presentTense ;
    Past_Time = pastTense ;
    Future_Time = futureTense ;
}
