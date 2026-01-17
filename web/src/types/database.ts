export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  public: {
    Tables: {
      age_classes: {
        Row: {
          code: string
          created_at: string | null
          gender: string
          id: string
          is_aggregate: boolean | null
          max_age: number | null
          min_age: number
          name: string
          name_en: string | null
          parent_class_id: string | null
          sort_order: number | null
          updated_at: string | null
        }
        Insert: {
          code: string
          gender: string
          id?: string
          min_age: number
          name: string
          max_age?: number | null
          name_en?: string | null
        }
        Update: {
          code?: string
          gender?: string
          min_age?: number
          name?: string
        }
        Relationships: []
      }
      athletes: {
        Row: {
          bio: string | null
          birth_date: string | null
          birth_year: number | null
          created_at: string | null
          current_club_id: string | null
          external_id: string | null
          first_name: string
          full_name: string | null
          gender: string | null
          id: string
          isonen_id: string | null
          last_name: string
          nationality: string | null
          profile_image_url: string | null
          updated_at: string | null
          verified: boolean | null
        }
        Insert: {
          first_name: string
          last_name: string
          id?: string
          gender?: string | null
          birth_date?: string | null
        }
        Update: {
          first_name?: string
          last_name?: string
          gender?: string | null
          birth_date?: string | null
        }
        Relationships: []
      }
      clubs: {
        Row: {
          active: boolean | null
          city: string | null
          county: string | null
          created_at: string | null
          federation_id: string | null
          id: string
          isonen_id: string | null
          name: string
          short_name: string | null
          updated_at: string | null
          website: string | null
        }
        Insert: {
          name: string
          id?: string
        }
        Update: {
          name?: string
        }
        Relationships: []
      }
      events: {
        Row: {
          category: Database["public"]["Enums"]["event_category"]
          code: string
          created_at: string | null
          gender: string | null
          id: string
          implement_specs: Json | null
          indoor: boolean | null
          name: string
          name_en: string | null
          result_type: Database["public"]["Enums"]["result_type"]
          sort_order: number | null
          updated_at: string | null
          wind_measured: boolean | null
        }
        Insert: {
          category: Database["public"]["Enums"]["event_category"]
          code: string
          name: string
          result_type: Database["public"]["Enums"]["result_type"]
          id?: string
        }
        Update: {
          category?: Database["public"]["Enums"]["event_category"]
          code?: string
          name?: string
          result_type?: Database["public"]["Enums"]["result_type"]
        }
        Relationships: []
      }
      meets: {
        Row: {
          city: string
          country: string | null
          created_at: string | null
          end_date: string | null
          id: string
          indoor: boolean
          isonen_id: string | null
          level: Database["public"]["Enums"]["meet_level"] | null
          name: string
          notes: string | null
          organizer_club_id: string | null
          organizer_name: string | null
          season_id: string | null
          start_date: string
          updated_at: string | null
          venue: string | null
          website: string | null
        }
        Insert: {
          city: string
          name: string
          start_date: string
          id?: string
          indoor?: boolean
        }
        Update: {
          city?: string
          name?: string
          start_date?: string
          indoor?: boolean
        }
        Relationships: []
      }
      results: {
        Row: {
          athlete_id: string
          attempts: Json | null
          club_id: string | null
          competition_age_class_id: string | null
          created_at: string | null
          date: string
          event_id: string
          heat_number: number | null
          hurdle_height_cm: number | null
          id: string
          implement_weight_kg: number | null
          import_batch_id: string | null
          is_championship_record: boolean | null
          is_national_record: boolean | null
          is_pb: boolean | null
          is_sb: boolean | null
          lane: number | null
          meet_id: string
          performance: string
          performance_value: number | null
          place: number | null
          reaction_time: number | null
          relay_members: Json | null
          round: Database["public"]["Enums"]["competition_round"] | null
          season_id: string
          source_id: string | null
          splits: Json | null
          status: Database["public"]["Enums"]["result_status"] | null
          updated_at: string | null
          verified: boolean | null
          wind: number | null
        }
        Insert: {
          athlete_id: string
          date: string
          event_id: string
          meet_id: string
          performance: string
          season_id: string
          id?: string
        }
        Update: {
          athlete_id?: string
          date?: string
          event_id?: string
          meet_id?: string
          performance?: string
          season_id?: string
        }
        Relationships: []
      }
      seasons: {
        Row: {
          created_at: string | null
          end_date: string | null
          id: string
          indoor: boolean
          name: string | null
          start_date: string | null
          year: number
        }
        Insert: {
          year: number
          id?: string
          indoor?: boolean
        }
        Update: {
          year?: number
          indoor?: boolean
        }
        Relationships: []
      }
      import_batches: {
        Row: {
          admin_notes: string | null
          created_at: string | null
          id: string
          imported_at: string | null
          matched_athletes: number | null
          meet_city: string | null
          meet_date: string | null
          meet_name: string | null
          name: string
          original_filename: string | null
          raw_data: Json | null
          reviewed_at: string | null
          reviewed_by: string | null
          row_count: number | null
          source_type: string | null
          status: string | null
          unmatched_athletes: number | null
          updated_at: string | null
          uploaded_at: string | null
          uploaded_by: string | null
          validation_errors: Json | null
          validation_warnings: Json | null
        }
        Insert: {
          name: string
          id?: string
        }
        Update: {
          name?: string
          status?: string | null
        }
        Relationships: []
      }
    }
    Views: {
      results_full: {
        Row: {
          athlete_id: string | null
          athlete_name: string | null
          birth_date: string | null
          club_id: string | null
          club_name: string | null
          date: string | null
          event_category: Database["public"]["Enums"]["event_category"] | null
          event_code: string | null
          event_id: string | null
          event_name: string | null
          first_name: string | null
          gender: string | null
          id: string | null
          is_national_record: boolean | null
          is_pb: boolean | null
          is_sb: boolean | null
          last_name: string | null
          meet_city: string | null
          meet_id: string | null
          meet_indoor: boolean | null
          meet_level: Database["public"]["Enums"]["meet_level"] | null
          meet_name: string | null
          performance: string | null
          performance_value: number | null
          place: number | null
          result_type: Database["public"]["Enums"]["result_type"] | null
          round: Database["public"]["Enums"]["competition_round"] | null
          season_id: string | null
          season_indoor: boolean | null
          season_name: string | null
          season_year: number | null
          status: Database["public"]["Enums"]["result_status"] | null
          verified: boolean | null
          wind: number | null
        }
        Relationships: []
      }
      personal_bests: {
        Row: {
          athlete_id: string | null
          athlete_name: string | null
          date: string | null
          event_code: string | null
          event_id: string | null
          event_name: string | null
          gender: string | null
          meet_id: string | null
          meet_name: string | null
          performance: string | null
          performance_value: number | null
          result_id: string | null
          result_type: Database["public"]["Enums"]["result_type"] | null
          wind: number | null
        }
        Relationships: []
      }
      season_bests: {
        Row: {
          athlete_id: string | null
          athlete_name: string | null
          date: string | null
          event_code: string | null
          event_id: string | null
          event_name: string | null
          meet_id: string | null
          performance: string | null
          performance_value: number | null
          result_id: string | null
          result_type: Database["public"]["Enums"]["result_type"] | null
          season_id: string | null
          season_name: string | null
          wind: number | null
        }
        Relationships: []
      }
      personal_bests_detailed: {
        Row: {
          athlete_id: string | null
          athlete_name: string | null
          date: string | null
          event_code: string | null
          event_id: string | null
          event_name: string | null
          event_sort_order: number | null
          gender: string | null
          is_indoor: boolean | null
          is_national_record: boolean | null
          meet_city: string | null
          meet_id: string | null
          meet_name: string | null
          performance: string | null
          performance_value: number | null
          result_id: string | null
          result_type: Database["public"]["Enums"]["result_type"] | null
          wind: number | null
        }
        Relationships: []
      }
    }
    Functions: {
      athletics_age: {
        Args: { birth_date: string; result_date: string }
        Returns: number
      }
      get_age_group: {
        Args: { birth_date: string; competition_date: string }
        Returns: string
      }
    }
    Enums: {
      competition_round:
        | "heat"
        | "quarter"
        | "semi"
        | "final"
        | "a_final"
        | "b_final"
        | "qualification"
      event_category:
        | "sprint"
        | "middle_distance"
        | "long_distance"
        | "hurdles"
        | "steeplechase"
        | "relay"
        | "jumps"
        | "throws"
        | "combined"
        | "race_walk"
      meet_level:
        | "local"
        | "regional"
        | "national"
        | "championship"
        | "international"
      result_status: "OK" | "DNS" | "DNF" | "DQ" | "NM"
      result_type: "time" | "distance" | "height" | "points"
    }
  }
}

// Helper types
export type Tables<T extends keyof Database["public"]["Tables"]> =
  Database["public"]["Tables"][T]["Row"]
export type Views<T extends keyof Database["public"]["Views"]> =
  Database["public"]["Views"][T]["Row"]
export type Enums<T extends keyof Database["public"]["Enums"]> =
  Database["public"]["Enums"][T]

// Convenience types
export type Athlete = Tables<"athletes">
export type Club = Tables<"clubs">
export type Event = Tables<"events">
export type Meet = Tables<"meets">
export type Result = Tables<"results">
export type Season = Tables<"seasons">
export type AgeClass = Tables<"age_classes">
export type ImportBatch = Tables<"import_batches">

export type ResultFull = Views<"results_full">
export type PersonalBest = Views<"personal_bests">
export type SeasonBest = Views<"season_bests">
export type PersonalBestDetailed = Views<"personal_bests_detailed">
