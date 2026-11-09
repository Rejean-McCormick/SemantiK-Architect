-- Semantic-to-GF typed candidate. No words from request are interpolated into GF trees.
abstract DefluensCore = {
  flags startcat = Output ;
  cat Output ; Subject ; Quality ; Kind ; EventV ; ActionV2 ; ObjectNP ; Place ; CommandV ; Polarity ; TimeRef ;
  fun
    RealizeAttribute : Subject -> Quality -> Polarity -> TimeRef -> Output ;
    RealizeClass : Subject -> Kind -> Polarity -> TimeRef -> Output ;
    RealizeEvent : Subject -> EventV -> Polarity -> TimeRef -> Output ;
    RealizeAction : Subject -> ActionV2 -> ObjectNP -> Polarity -> TimeRef -> Output ;
    RealizeLocation : Subject -> Place -> Polarity -> TimeRef -> Output ;
    RealizeDirective : CommandV -> Polarity -> Output ;
    Mira_Subject, Lea_Subject, Noa_Subject : Subject ;
    Ready_Quality, Calm_Quality, Absent_Quality, Available_Quality : Quality ;
    Guide_Kind, Artist_Kind, Scientist_Kind : Kind ;
    Work_Event, Walk_Event, Speak_Event : EventV ;
    Carry_Action, Watch_Action, Visit_Action : ActionV2 ;
    Book_Object, Document_Object, Flower_Object : ObjectNP ;
    Here_Place, There_Place, InParis_Place : Place ;
    Wait_Command, Walk_Command, Speak_Command : CommandV ;
    Positive_Polarity, Negative_Polarity : Polarity ;
    Present_Time, Past_Time, Future_Time : TimeRef ;
}
