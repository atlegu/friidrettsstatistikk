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
          created_at?: string | null
          gender: string
          id?: string
          is_aggregate?: boolean | null
          max_age?: number | null
          min_age: number
          name: string
          name_en?: string | null
          parent_class_id?: string | null
          sort_order?: number | null
          updated_at?: string | null
        }
        Update: {
          code?: string
          created_at?: string | null
          gender?: string
          id?: string
          is_aggregate?: boolean | null
          max_age?: number | null
          min_age?: number
          name?: string
          name_en?: string | null
          parent_class_id?: string | null
          sort_order?: number | null
          updated_at?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "age_classes_parent_class_id_fkey"
            columns: ["parent_class_id"]
            isOneToOne: false
            referencedRelation: "age_classes"
            referencedColumns: ["id"]
          },
        ]
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
          verified_at: string | null
          verified_by: string | null
        }
        Insert: {
          bio?: string | null
          birth_date?: string | null
          birth_year?: number | null
          created_at?: string | null
          current_club_id?: string | null
          external_id?: string | null
          first_name: string
          full_name?: string | null
          gender?: string | null
          id?: string
          isonen_id?: string | null
          last_name: string
          nationality?: string | null
          profile_image_url?: string | null
          updated_at?: string | null
          verified?: boolean | null
          verified_at?: string | null
          verified_by?: string | null
        }
        Update: {
          bio?: string | null
          birth_date?: string | null
          birth_year?: number | null
          created_at?: string | null
          current_club_id?: string | null
          external_id?: string | null
          first_name?: string
          full_name?: string | null
          gender?: string | null
          id?: string
          isonen_id?: string | null
          last_name?: string
          nationality?: string | null
          profile_image_url?: string | null
          updated_at?: string | null
          verified?: boolean | null
          verified_at?: string | null
          verified_by?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "athletes_current_club_id_fkey"
            columns: ["current_club_id"]
            isOneToOne: false
            referencedRelation: "clubs"
            referencedColumns: ["id"]
          },
        ]
      }
      club_memberships: {
        Row: {
          athlete_id: string
          club_id: string
          created_at: string | null
          from_date: string
          id: string
          to_date: string | null
        }
        Insert: {
          athlete_id: string
          club_id: string
          created_at?: string | null
          from_date: string
          id?: string
          to_date?: string | null
        }
        Update: {
          athlete_id?: string
          club_id?: string
          created_at?: string | null
          from_date?: string
          id?: string
          to_date?: string | null
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
          active?: boolean | null
          city?: string | null
          county?: string | null
          created_at?: string | null
          federation_id?: string | null
          id?: string
          isonen_id?: string | null
          name: string
          short_name?: string | null
          updated_at?: string | null
          website?: string | null
        }
        Update: {
          active?: boolean | null
          city?: string | null
          county?: string | null
          created_at?: string | null
          federation_id?: string | null
          id?: string
          isonen_id?: string | null
          name?: string
          short_name?: string | null
          updated_at?: string | null
          website?: string | null
        }
        Relationships: []
      }
      event_specifications: {
        Row: {
          age_class_id: string
          barrier_height_cm: number | null
          created_at: string | null
          event_id: string
          hurdle_count: number | null
          hurdle_first_m: number | null
          hurdle_height_cm: number | null
          hurdle_last_m: number | null
          hurdle_spacing_m: number | null
          id: string
          implement_length_cm: number | null
          implement_weight_kg: number | null
          is_default: boolean | null
          landing_zone_cm: number | null
          notes: string | null
          updated_at: string | null
          water_jump: boolean | null
        }
        Insert: {
          age_class_id: string
          barrier_height_cm?: number | null
          created_at?: string | null
          event_id: string
          hurdle_count?: number | null
          hurdle_first_m?: number | null
          hurdle_height_cm?: number | null
          hurdle_last_m?: number | null
          hurdle_spacing_m?: number | null
          id?: string
          implement_length_cm?: number | null
          implement_weight_kg?: number | null
          is_default?: boolean | null
          landing_zone_cm?: number | null
          notes?: string | null
          updated_at?: string | null
          water_jump?: boolean | null
        }
        Update: {
          age_class_id?: string
          barrier_height_cm?: number | null
          created_at?: string | null
          event_id?: string
          hurdle_count?: number | null
          hurdle_first_m?: number | null
          hurdle_height_cm?: number | null
          hurdle_last_m?: number | null
          hurdle_spacing_m?: number | null
          id?: string
          implement_length_cm?: number | null
          implement_weight_kg?: number | null
          is_default?: boolean | null
          landing_zone_cm?: number | null
          notes?: string | null
          updated_at?: string | null
          water_jump?: boolean | null
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
          created_at?: string | null
          gender?: string | null
          id?: string
          implement_specs?: Json | null
          indoor?: boolean | null
          name: string
          name_en?: string | null
          result_type: Database["public"]["Enums"]["result_type"]
          sort_order?: number | null
          updated_at?: string | null
          wind_measured?: boolean | null
        }
        Update: {
          category?: Database["public"]["Enums"]["event_category"]
          code?: string
          created_at?: string | null
          gender?: string | null
          id?: string
          implement_specs?: Json | null
          indoor?: boolean | null
          name?: string
          name_en?: string | null
          result_type?: Database["public"]["Enums"]["result_type"]
          sort_order?: number | null
          updated_at?: string | null
          wind_measured?: boolean | null
        }
        Relationships: []
      }
      federations: {
        Row: {
          country: string | null
          created_at: string | null
          id: string
          name: string
          parent_id: string | null
          short_name: string | null
          updated_at: string | null
        }
        Insert: {
          country?: string | null
          created_at?: string | null
          id?: string
          name: string
          parent_id?: string | null
          short_name?: string | null
          updated_at?: string | null
        }
        Update: {
          country?: string | null
          created_at?: string | null
          id?: string
          name?: string
          parent_id?: string | null
          short_name?: string | null
          updated_at?: string | null
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
          admin_notes?: string | null
          created_at?: string | null
          id?: string
          imported_at?: string | null
          matched_athletes?: number | null
          meet_city?: string | null
          meet_date?: string | null
          meet_name?: string | null
          name: string
          original_filename?: string | null
          raw_data?: Json | null
          reviewed_at?: string | null
          reviewed_by?: string | null
          row_count?: number | null
          source_type?: string | null
          status?: string | null
          unmatched_athletes?: number | null
          updated_at?: string | null
          uploaded_at?: string | null
          uploaded_by?: string | null
          validation_errors?: Json | null
          validation_warnings?: Json | null
        }
        Update: {
          admin_notes?: string | null
          created_at?: string | null
          id?: string
          imported_at?: string | null
          matched_athletes?: number | null
          meet_city?: string | null
          meet_date?: string | null
          meet_name?: string | null
          name?: string
          original_filename?: string | null
          raw_data?: Json | null
          reviewed_at?: string | null
          reviewed_by?: string | null
          row_count?: number | null
          source_type?: string | null
          status?: string | null
          unmatched_athletes?: number | null
          updated_at?: string | null
          uploaded_at?: string | null
          uploaded_by?: string | null
          validation_errors?: Json | null
          validation_warnings?: Json | null
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
          country?: string | null
          created_at?: string | null
          end_date?: string | null
          id?: string
          indoor?: boolean
          isonen_id?: string | null
          level?: Database["public"]["Enums"]["meet_level"] | null
          name: string
          notes?: string | null
          organizer_club_id?: string | null
          organizer_name?: string | null
          season_id?: string | null
          start_date: string
          updated_at?: string | null
          venue?: string | null
          website?: string | null
        }
        Update: {
          city?: string
          country?: string | null
          created_at?: string | null
          end_date?: string | null
          id?: string
          indoor?: boolean
          isonen_id?: string | null
          level?: Database["public"]["Enums"]["meet_level"] | null
          name?: string
          notes?: string | null
          organizer_club_id?: string | null
          organizer_name?: string | null
          season_id?: string | null
          start_date?: string
          updated_at?: string | null
          venue?: string | null
          website?: string | null
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
          verified_at: string | null
          verified_by: string | null
          wind: number | null
        }
        Insert: {
          athlete_id: string
          attempts?: Json | null
          club_id?: string | null
          competition_age_class_id?: string | null
          created_at?: string | null
          date: string
          event_id: string
          heat_number?: number | null
          hurdle_height_cm?: number | null
          id?: string
          implement_weight_kg?: number | null
          import_batch_id?: string | null
          is_championship_record?: boolean | null
          is_national_record?: boolean | null
          is_pb?: boolean | null
          is_sb?: boolean | null
          lane?: number | null
          meet_id: string
          performance: string
          performance_value?: number | null
          place?: number | null
          reaction_time?: number | null
          relay_members?: Json | null
          round?: Database["public"]["Enums"]["competition_round"] | null
          season_id: string
          source_id?: string | null
          splits?: Json | null
          status?: Database["public"]["Enums"]["result_status"] | null
          updated_at?: string | null
          verified?: boolean | null
          verified_at?: string | null
          verified_by?: string | null
          wind?: number | null
        }
        Update: {
          athlete_id?: string
          attempts?: Json | null
          club_id?: string | null
          competition_age_class_id?: string | null
          created_at?: string | null
          date?: string
          event_id?: string
          heat_number?: number | null
          hurdle_height_cm?: number | null
          id?: string
          implement_weight_kg?: number | null
          import_batch_id?: string | null
          is_championship_record?: boolean | null
          is_national_record?: boolean | null
          is_pb?: boolean | null
          is_sb?: boolean | null
          lane?: number | null
          meet_id?: string
          performance?: string
          performance_value?: number | null
          place?: number | null
          reaction_time?: number | null
          relay_members?: Json | null
          round?: Database["public"]["Enums"]["competition_round"] | null
          season_id?: string
          source_id?: string | null
          splits?: Json | null
          status?: Database["public"]["Enums"]["result_status"] | null
          updated_at?: string | null
          verified?: boolean | null
          verified_at?: string | null
          verified_by?: string | null
          wind?: number | null
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
          created_at?: string | null
          end_date?: string | null
          id?: string
          indoor?: boolean
          name?: string | null
          start_date?: string | null
          year: number
        }
        Update: {
          created_at?: string | null
          end_date?: string | null
          id?: string
          indoor?: boolean
          name?: string | null
          start_date?: string | null
          year?: number
        }
        Relationships: []
      }
      sources: {
        Row: {
          id: string
          imported_at: string | null
          imported_by: string | null
          metadata: Json | null
          name: string
          original_file_name: string | null
          original_url: string | null
          source_type: string | null
        }
        Insert: {
          id?: string
          imported_at?: string | null
          imported_by?: string | null
          metadata?: Json | null
          name: string
          original_file_name?: string | null
          original_url?: string | null
          source_type?: string | null
        }
        Update: {
          id?: string
          imported_at?: string | null
          imported_by?: string | null
          metadata?: Json | null
          name?: string
          original_file_name?: string | null
          original_url?: string | null
          source_type?: string | null
        }
        Relationships: []
      }
      user_profiles: {
        Row: {
          created_at: string | null
          display_name: string | null
          email: string
          id: string
          role: string
          updated_at: string | null
          user_id: string | null
        }
        Insert: {
          created_at?: string | null
          display_name?: string | null
          email: string
          id?: string
          role?: string
          updated_at?: string | null
          user_id?: string | null
        }
        Update: {
          created_at?: string | null
          display_name?: string | null
          email?: string
          id?: string
          role?: string
          updated_at?: string | null
          user_id?: string | null
        }
        Relationships: []
      }
    }
    Views: {
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
      results_full: {
        Row: {
          age_group: string | null
          athlete_id: string | null
          athlete_name: string | null
          attempts: Json | null
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
          reaction_time: number | null
          result_type: Database["public"]["Enums"]["result_type"] | null
          round: Database["public"]["Enums"]["competition_round"] | null
          season_id: string | null
          season_indoor: boolean | null
          season_name: string | null
          season_year: number | null
          splits: Json | null
          status: Database["public"]["Enums"]["result_status"] | null
          verified: boolean | null
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
    }
    Functions: {
      athletics_age: {
        Args: { birth_date: string; result_date: string }
        Returns: number
      }
      format_performance: {
        Args: {
          perf_value: number
          res_type: Database["public"]["Enums"]["result_type"]
        }
        Returns: string
      }
      get_age_classes: {
        Args: {
          athlete_gender: string
          birth_date: string
          result_date: string
        }
        Returns: {
          age_class_code: string
          age_class_id: string
        }[]
      }
      get_age_group: {
        Args: { birth_date: string; competition_date: string }
        Returns: string
      }
      is_admin: { Args: Record<PropertyKey, never>; Returns: boolean }
      parse_performance: {
        Args: {
          perf: string
          res_type: Database["public"]["Enums"]["result_type"]
        }
        Returns: number
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
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

type DefaultSchema = Database[Extract<keyof Database, "public">]

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    | { schema: keyof Database },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof Database
  }
    ? keyof (Database[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        Database[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof Database
}
  ? (Database[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
      Database[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R
    }
    ? R
    : never
  : DefaultSchemaTableNameOrOptions extends keyof (DefaultSchema["Tables"] &
        DefaultSchema["Views"])
    ? (DefaultSchema["Tables"] &
        DefaultSchema["Views"])[DefaultSchemaTableNameOrOptions] extends {
        Row: infer R
      }
      ? R
      : never
    : never

export type TablesInsert<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof Database },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof Database
  }
    ? keyof Database[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof Database
}
  ? Database[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I
    }
    ? I
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Insert: infer I
      }
      ? I
      : never
    : never

export type TablesUpdate<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof Database },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof Database
  }
    ? keyof Database[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof Database
}
  ? Database[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U
    }
    ? U
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Update: infer U
      }
      ? U
      : never
    : never

export type Enums<
  DefaultSchemaEnumNameOrOptions extends
    | keyof DefaultSchema["Enums"]
    | { schema: keyof Database },
  EnumName extends DefaultSchemaEnumNameOrOptions extends {
    schema: keyof Database
  }
    ? keyof Database[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never = never,
> = DefaultSchemaEnumNameOrOptions extends {
  schema: keyof Database
}
  ? Database[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
    ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
    : never
