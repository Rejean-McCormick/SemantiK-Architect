-- Ars Magna Defluens / SemantiK Architect typed attribute candidate.
-- SemantiK owns semantic planning; GF/RGL owns realization.
abstract DefluensAttribute = {
  flags startcat = Output ;
  cat Output ; Subject ; Quality ; Polarity ; TimeRef ;
  fun
    RealizeAttribute : Subject -> Quality -> Polarity -> TimeRef -> Output ;
    Mira_Subject, Lea_Subject, Noa_Subject : Subject ;
    Ready_Quality, Calm_Quality, Absent_Quality, Available_Quality : Quality ;
    Positive_Polarity, Negative_Polarity : Polarity ;
    Present_Time, Past_Time, Future_Time : TimeRef ;
}
