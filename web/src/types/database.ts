export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  // Allows to automatically instantiate createClient with right options
  // instead of createClient<Database, { PostgrestVersion: 'XX' }>(URL, KEY)
  __InternalSupabase: {
    PostgrestVersion: "14.5"
  }
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
          {
            foreignKeyName: "athletes_current_club_id_fkey"
            columns: ["current_club_id"]
            isOneToOne: false
            referencedRelation: "klubb_bruk"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "athletes_current_club_id_fkey"
            columns: ["current_club_id"]
            isOneToOne: false
            referencedRelation: "klubber_med_statistikk"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "athletes_current_club_id_fkey"
            columns: ["current_club_id"]
            isOneToOne: false
            referencedRelation: "results_full"
            referencedColumns: ["club_id"]
          },
        ]
      }
      championship_medals: {
        Row: {
          athlete_id: string | null
          athlete_name: string
          championship_type: string
          club_name: string | null
          created_at: string | null
          event_name: string
          gender: string
          id: string
          medal: string
          performance: string | null
          source_url: string | null
          year: number
        }
        Insert: {
          athlete_id?: string | null
          athlete_name: string
          championship_type: string
          club_name?: string | null
          created_at?: string | null
          event_name: string
          gender: string
          id?: string
          medal: string
          performance?: string | null
          source_url?: string | null
          year: number
        }
        Update: {
          athlete_id?: string | null
          athlete_name?: string
          championship_type?: string
          club_name?: string | null
          created_at?: string | null
          event_name?: string
          gender?: string
          id?: string
          medal?: string
          performance?: string | null
          source_url?: string | null
          year?: number
        }
        Relationships: [
          {
            foreignKeyName: "championship_medals_athlete_id_fkey"
            columns: ["athlete_id"]
            isOneToOne: false
            referencedRelation: "athletes"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "championship_medals_athlete_id_fkey"
            columns: ["athlete_id"]
            isOneToOne: false
            referencedRelation: "personal_bests_detailed"
            referencedColumns: ["athlete_id"]
          },
          {
            foreignKeyName: "championship_medals_athlete_id_fkey"
            columns: ["athlete_id"]
            isOneToOne: false
            referencedRelation: "results_full"
            referencedColumns: ["athlete_id"]
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
        Relationships: [
          {
            foreignKeyName: "club_memberships_athlete_id_fkey"
            columns: ["athlete_id"]
            isOneToOne: false
            referencedRelation: "athletes"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "club_memberships_athlete_id_fkey"
            columns: ["athlete_id"]
            isOneToOne: false
            referencedRelation: "personal_bests_detailed"
            referencedColumns: ["athlete_id"]
          },
          {
            foreignKeyName: "club_memberships_athlete_id_fkey"
            columns: ["athlete_id"]
            isOneToOne: false
            referencedRelation: "results_full"
            referencedColumns: ["athlete_id"]
          },
          {
            foreignKeyName: "club_memberships_club_id_fkey"
            columns: ["club_id"]
            isOneToOne: false
            referencedRelation: "clubs"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "club_memberships_club_id_fkey"
            columns: ["club_id"]
            isOneToOne: false
            referencedRelation: "klubb_bruk"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "club_memberships_club_id_fkey"
            columns: ["club_id"]
            isOneToOne: false
            referencedRelation: "klubber_med_statistikk"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "club_memberships_club_id_fkey"
            columns: ["club_id"]
            isOneToOne: false
            referencedRelation: "results_full"
            referencedColumns: ["club_id"]
          },
        ]
      }
      clubs: {
        Row: {
          active: boolean | null
          city: string | null
          club_type: Database["public"]["Enums"]["club_type"] | null
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
          club_type?: Database["public"]["Enums"]["club_type"] | null
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
          club_type?: Database["public"]["Enums"]["club_type"] | null
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
        Relationships: [
          {
            foreignKeyName: "clubs_federation_id_fkey"
            columns: ["federation_id"]
            isOneToOne: false
            referencedRelation: "federations"
            referencedColumns: ["id"]
          },
        ]
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
        Relationships: [
          {
            foreignKeyName: "event_specifications_age_class_id_fkey"
            columns: ["age_class_id"]
            isOneToOne: false
            referencedRelation: "age_classes"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "event_specifications_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "events"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "event_specifications_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "personal_bests_detailed"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "event_specifications_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "results_full"
            referencedColumns: ["event_id"]
          },
        ]
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
        Relationships: [
          {
            foreignKeyName: "federations_parent_id_fkey"
            columns: ["parent_id"]
            isOneToOne: false
            referencedRelation: "federations"
            referencedColumns: ["id"]
          },
        ]
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
      klubb_ordformer: {
        Row: {
          form: string
          kanonisk: string
        }
        Insert: {
          form: string
          kanonisk: string
        }
        Update: {
          form?: string
          kanonisk?: string
        }
        Relationships: []
      }
      meets: {
        Row: {
          city: string
          country: string | null
          created_at: string | null
          end_date: string | null
          external_id: string | null
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
          external_id?: string | null
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
          external_id?: string | null
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
        Relationships: [
          {
            foreignKeyName: "meets_organizer_club_id_fkey"
            columns: ["organizer_club_id"]
            isOneToOne: false
            referencedRelation: "clubs"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "meets_organizer_club_id_fkey"
            columns: ["organizer_club_id"]
            isOneToOne: false
            referencedRelation: "klubb_bruk"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "meets_organizer_club_id_fkey"
            columns: ["organizer_club_id"]
            isOneToOne: false
            referencedRelation: "klubber_med_statistikk"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "meets_organizer_club_id_fkey"
            columns: ["organizer_club_id"]
            isOneToOne: false
            referencedRelation: "results_full"
            referencedColumns: ["club_id"]
          },
          {
            foreignKeyName: "meets_season_id_fkey"
            columns: ["season_id"]
            isOneToOne: false
            referencedRelation: "results_full"
            referencedColumns: ["season_id"]
          },
          {
            foreignKeyName: "meets_season_id_fkey"
            columns: ["season_id"]
            isOneToOne: false
            referencedRelation: "seasons"
            referencedColumns: ["id"]
          },
        ]
      }
      opprydding_stevnepar: {
        Row: {
          behold: string | null
          dubletter: number | null
          fjern: string | null
          m1: string | null
          m1_dato: string | null
          m1_ext: string | null
          m1_navn: string | null
          m1_res: number | null
          m2: string | null
          m2_dato: string | null
          m2_ext: string | null
          m2_navn: string | null
          m2_res: number | null
          overlapp_pst: number | null
          relasjon: string | null
          resultat: Json | null
          utfort: string | null
          vedtak: string | null
        }
        Insert: {
          behold?: string | null
          dubletter?: number | null
          fjern?: string | null
          m1?: string | null
          m1_dato?: string | null
          m1_ext?: string | null
          m1_navn?: string | null
          m1_res?: number | null
          m2?: string | null
          m2_dato?: string | null
          m2_ext?: string | null
          m2_navn?: string | null
          m2_res?: number | null
          overlapp_pst?: number | null
          relasjon?: string | null
          resultat?: Json | null
          utfort?: string | null
          vedtak?: string | null
        }
        Update: {
          behold?: string | null
          dubletter?: number | null
          fjern?: string | null
          m1?: string | null
          m1_dato?: string | null
          m1_ext?: string | null
          m1_navn?: string | null
          m1_res?: number | null
          m2?: string | null
          m2_dato?: string | null
          m2_ext?: string | null
          m2_navn?: string | null
          m2_res?: number | null
          overlapp_pst?: number | null
          relasjon?: string | null
          resultat?: Json | null
          utfort?: string | null
          vedtak?: string | null
        }
        Relationships: []
      }
      profiles: {
        Row: {
          ai_requests_reset_at: string | null
          ai_requests_today: number | null
          avatar_url: string | null
          created_at: string | null
          email: string | null
          full_name: string | null
          id: string
          is_admin: boolean | null
          stripe_customer_id: string | null
          subscription_expires_at: string | null
          subscription_tier: string | null
          updated_at: string | null
        }
        Insert: {
          ai_requests_reset_at?: string | null
          ai_requests_today?: number | null
          avatar_url?: string | null
          created_at?: string | null
          email?: string | null
          full_name?: string | null
          id: string
          is_admin?: boolean | null
          stripe_customer_id?: string | null
          subscription_expires_at?: string | null
          subscription_tier?: string | null
          updated_at?: string | null
        }
        Update: {
          ai_requests_reset_at?: string | null
          ai_requests_today?: number | null
          avatar_url?: string | null
          created_at?: string | null
          email?: string | null
          full_name?: string | null
          id?: string
          is_admin?: boolean | null
          stripe_customer_id?: string | null
          subscription_expires_at?: string | null
          subscription_tier?: string | null
          updated_at?: string | null
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
          is_manual_time: boolean | null
          is_national_record: boolean | null
          is_pb: boolean | null
          is_sb: boolean | null
          is_wind_legal: boolean | null
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
          source_marker: string | null
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
          is_manual_time?: boolean | null
          is_national_record?: boolean | null
          is_pb?: boolean | null
          is_sb?: boolean | null
          is_wind_legal?: boolean | null
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
          source_marker?: string | null
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
          is_manual_time?: boolean | null
          is_national_record?: boolean | null
          is_pb?: boolean | null
          is_sb?: boolean | null
          is_wind_legal?: boolean | null
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
          source_marker?: string | null
          splits?: Json | null
          status?: Database["public"]["Enums"]["result_status"] | null
          updated_at?: string | null
          verified?: boolean | null
          verified_at?: string | null
          verified_by?: string | null
          wind?: number | null
        }
        Relationships: [
          {
            foreignKeyName: "results_athlete_id_fkey"
            columns: ["athlete_id"]
            isOneToOne: false
            referencedRelation: "athletes"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "results_athlete_id_fkey"
            columns: ["athlete_id"]
            isOneToOne: false
            referencedRelation: "personal_bests_detailed"
            referencedColumns: ["athlete_id"]
          },
          {
            foreignKeyName: "results_athlete_id_fkey"
            columns: ["athlete_id"]
            isOneToOne: false
            referencedRelation: "results_full"
            referencedColumns: ["athlete_id"]
          },
          {
            foreignKeyName: "results_club_id_fkey"
            columns: ["club_id"]
            isOneToOne: false
            referencedRelation: "clubs"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "results_club_id_fkey"
            columns: ["club_id"]
            isOneToOne: false
            referencedRelation: "klubb_bruk"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "results_club_id_fkey"
            columns: ["club_id"]
            isOneToOne: false
            referencedRelation: "klubber_med_statistikk"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "results_club_id_fkey"
            columns: ["club_id"]
            isOneToOne: false
            referencedRelation: "results_full"
            referencedColumns: ["club_id"]
          },
          {
            foreignKeyName: "results_competition_age_class_id_fkey"
            columns: ["competition_age_class_id"]
            isOneToOne: false
            referencedRelation: "age_classes"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "results_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "events"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "results_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "personal_bests_detailed"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "results_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "results_full"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "results_import_batch_id_fkey"
            columns: ["import_batch_id"]
            isOneToOne: false
            referencedRelation: "import_batches"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "results_meet_id_fkey"
            columns: ["meet_id"]
            isOneToOne: false
            referencedRelation: "meets"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "results_meet_id_fkey"
            columns: ["meet_id"]
            isOneToOne: false
            referencedRelation: "personal_bests_detailed"
            referencedColumns: ["meet_id"]
          },
          {
            foreignKeyName: "results_meet_id_fkey"
            columns: ["meet_id"]
            isOneToOne: false
            referencedRelation: "results_full"
            referencedColumns: ["meet_id"]
          },
          {
            foreignKeyName: "results_season_id_fkey"
            columns: ["season_id"]
            isOneToOne: false
            referencedRelation: "results_full"
            referencedColumns: ["season_id"]
          },
          {
            foreignKeyName: "results_season_id_fkey"
            columns: ["season_id"]
            isOneToOne: false
            referencedRelation: "seasons"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "results_source_id_fkey"
            columns: ["source_id"]
            isOneToOne: false
            referencedRelation: "sources"
            referencedColumns: ["id"]
          },
        ]
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
      vedlikehold: {
        Row: {
          nokkel: string
          sist_oppdatert: string | null
          utdatert_siden: string | null
        }
        Insert: {
          nokkel: string
          sist_oppdatert?: string | null
          utdatert_siden?: string | null
        }
        Update: {
          nokkel?: string
          sist_oppdatert?: string | null
          utdatert_siden?: string | null
        }
        Relationships: []
      }
    }
    Views: {
      aktivitet_grunnlag: {
        Row: {
          aar: number | null
          alder: string | null
          athlete_id: string | null
          kategori: string | null
          kjonn: string | null
          meet_id: string | null
          starter: number | null
        }
        Relationships: [
          {
            foreignKeyName: "results_athlete_id_fkey"
            columns: ["athlete_id"]
            isOneToOne: false
            referencedRelation: "athletes"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "results_athlete_id_fkey"
            columns: ["athlete_id"]
            isOneToOne: false
            referencedRelation: "personal_bests_detailed"
            referencedColumns: ["athlete_id"]
          },
          {
            foreignKeyName: "results_athlete_id_fkey"
            columns: ["athlete_id"]
            isOneToOne: false
            referencedRelation: "results_full"
            referencedColumns: ["athlete_id"]
          },
          {
            foreignKeyName: "results_meet_id_fkey"
            columns: ["meet_id"]
            isOneToOne: false
            referencedRelation: "meets"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "results_meet_id_fkey"
            columns: ["meet_id"]
            isOneToOne: false
            referencedRelation: "personal_bests_detailed"
            referencedColumns: ["meet_id"]
          },
          {
            foreignKeyName: "results_meet_id_fkey"
            columns: ["meet_id"]
            isOneToOne: false
            referencedRelation: "results_full"
            referencedColumns: ["meet_id"]
          },
        ]
      }
      aktivitet_klubb: {
        Row: {
          aar: number | null
          club_id: string | null
          resultater: number | null
        }
        Relationships: [
          {
            foreignKeyName: "results_club_id_fkey"
            columns: ["club_id"]
            isOneToOne: false
            referencedRelation: "clubs"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "results_club_id_fkey"
            columns: ["club_id"]
            isOneToOne: false
            referencedRelation: "klubb_bruk"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "results_club_id_fkey"
            columns: ["club_id"]
            isOneToOne: false
            referencedRelation: "klubber_med_statistikk"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "results_club_id_fkey"
            columns: ["club_id"]
            isOneToOne: false
            referencedRelation: "results_full"
            referencedColumns: ["club_id"]
          },
        ]
      }
      klubb_bruk: {
        Row: {
          city: string | null
          club_type: Database["public"]["Enums"]["club_type"] | null
          fra_ar: number | null
          id: string | null
          name: string | null
          resultater: number | null
          short_name: string | null
          sokenokkel: string | null
          til_ar: number | null
          utovere: number | null
        }
        Relationships: []
      }
      klubber_med_statistikk: {
        Row: {
          active: boolean | null
          antall_resultater: number | null
          antall_utovere: number | null
          city: string | null
          club_type: Database["public"]["Enums"]["club_type"] | null
          county: string | null
          created_at: string | null
          forste_resultat: string | null
          id: string | null
          name: string | null
          short_name: string | null
          siste_resultat: string | null
          website: string | null
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
        Relationships: [
          {
            foreignKeyName: "results_athlete_id_fkey"
            columns: ["athlete_id"]
            isOneToOne: false
            referencedRelation: "athletes"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "results_athlete_id_fkey"
            columns: ["athlete_id"]
            isOneToOne: false
            referencedRelation: "personal_bests_detailed"
            referencedColumns: ["athlete_id"]
          },
          {
            foreignKeyName: "results_athlete_id_fkey"
            columns: ["athlete_id"]
            isOneToOne: false
            referencedRelation: "results_full"
            referencedColumns: ["athlete_id"]
          },
          {
            foreignKeyName: "results_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "events"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "results_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "personal_bests_detailed"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "results_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "results_full"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "results_meet_id_fkey"
            columns: ["meet_id"]
            isOneToOne: false
            referencedRelation: "meets"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "results_meet_id_fkey"
            columns: ["meet_id"]
            isOneToOne: false
            referencedRelation: "personal_bests_detailed"
            referencedColumns: ["meet_id"]
          },
          {
            foreignKeyName: "results_meet_id_fkey"
            columns: ["meet_id"]
            isOneToOne: false
            referencedRelation: "results_full"
            referencedColumns: ["meet_id"]
          },
        ]
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
          javelin_spec: string | null
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
      plattform_statistikk: {
        Row: {
          antall_klubber: number | null
          antall_resultater: number | null
          antall_stevner: number | null
          antall_utovere: number | null
          id: number | null
          oppdatert: string | null
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
          club_type: Database["public"]["Enums"]["club_type"] | null
          date: string | null
          event_category: Database["public"]["Enums"]["event_category"] | null
          event_code: string | null
          event_id: string | null
          event_name: string | null
          first_name: string | null
          gender: string | null
          id: string | null
          is_manual_time: boolean | null
          is_national_record: boolean | null
          is_pb: boolean | null
          is_sb: boolean | null
          is_wind_legal: boolean | null
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
        Relationships: [
          {
            foreignKeyName: "results_athlete_id_fkey"
            columns: ["athlete_id"]
            isOneToOne: false
            referencedRelation: "athletes"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "results_athlete_id_fkey"
            columns: ["athlete_id"]
            isOneToOne: false
            referencedRelation: "personal_bests_detailed"
            referencedColumns: ["athlete_id"]
          },
          {
            foreignKeyName: "results_athlete_id_fkey"
            columns: ["athlete_id"]
            isOneToOne: false
            referencedRelation: "results_full"
            referencedColumns: ["athlete_id"]
          },
          {
            foreignKeyName: "results_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "events"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "results_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "personal_bests_detailed"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "results_event_id_fkey"
            columns: ["event_id"]
            isOneToOne: false
            referencedRelation: "results_full"
            referencedColumns: ["event_id"]
          },
          {
            foreignKeyName: "results_meet_id_fkey"
            columns: ["meet_id"]
            isOneToOne: false
            referencedRelation: "meets"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "results_meet_id_fkey"
            columns: ["meet_id"]
            isOneToOne: false
            referencedRelation: "personal_bests_detailed"
            referencedColumns: ["meet_id"]
          },
          {
            foreignKeyName: "results_meet_id_fkey"
            columns: ["meet_id"]
            isOneToOne: false
            referencedRelation: "results_full"
            referencedColumns: ["meet_id"]
          },
          {
            foreignKeyName: "results_season_id_fkey"
            columns: ["season_id"]
            isOneToOne: false
            referencedRelation: "results_full"
            referencedColumns: ["season_id"]
          },
          {
            foreignKeyName: "results_season_id_fkey"
            columns: ["season_id"]
            isOneToOne: false
            referencedRelation: "seasons"
            referencedColumns: ["id"]
          },
        ]
      }
    }
    Functions: {
      aktivitet_alder: {
        Args: { p_aar: number; p_kategori?: string; p_kjonn?: string }
        Returns: {
          alder: string
          unike: number
        }[]
      }
      aktivitet_klubber: {
        Args: { p_fra: number; p_til: number }
        Returns: {
          aar: number
          aktive: number
          alle: number
        }[]
      }
      aktivitet_per_aar: {
        Args: {
          p_alder?: string
          p_fra: number
          p_kategori?: string
          p_kjonn?: string
          p_til: number
        }
        Returns: {
          aar: number
          kvinner: number
          menn: number
          starter: number
          stevner: number
          unike: number
          unike_ungdom: number
        }[]
      }
      analyse_active_athletes: {
        Args: { from_year: number; to_year: number }
        Returns: {
          age_band: string
          gender: string
          n_athletes: number
          yr: number
        }[]
      }
      analyse_active_by_age: {
        Args: { from_year: number; to_year: number }
        Returns: {
          age: number
          gender: string
          n_athletes: number
          yr: number
        }[]
      }
      analyse_debut: {
        Args: { from_year: number; to_year: number }
        Returns: {
          debut_age: number
          gender: string
          n: number
          yr: number
        }[]
      }
      analyse_event_trend: {
        Args: {
          p_age_hi?: number
          p_age_lo?: number
          p_event_code: string
          p_from_year: number
          p_higher_better: boolean
          p_max_v: number
          p_min_v: number
          p_outdoor_only?: boolean
          p_to_year: number
        }
        Returns: {
          best_value: number
          gender: string
          n_athletes: number
          rank100_value: number
          rank25_value: number
          rank50_value: number
          top10_avg: number
          yr: number
        }[]
      }
      analyse_survival: {
        Args: {
          p_cohort_from: number
          p_cohort_to: number
          p_max_age?: number
          p_start_age: number
        }
        Returns: {
          age: number
          cohort_year: number
          gender: string
          n_active: number
        }[]
      }
      athletics_age: {
        Args: { birth_date: string; result_date: string }
        Returns: number
      }
      check_is_admin: { Args: { check_user_id: string }; Returns: boolean }
      er_vindpaavirket: { Args: { p_code: string }; Returns: boolean }
      execute_readonly_query: { Args: { query_text: string }; Returns: Json }
      felles_utovere_klubber: {
        Args: { a: string; b: string }
        Returns: {
          antall: number
        }[]
      }
      finn_feil_gjeldende_klubb: {
        Args: { fra: string; til: string }
        Returns: {
          antall_i_sesongen: number
          athlete_id: string
          klubb_na: string
          klubb_na_navn: string
          klubb_riktig: string
          klubb_riktig_navn: string
          navn: string
          siste_sesong: number
        }[]
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
      get_all_time_best: {
        Args: {
          p_age_groups?: string[]
          p_ascending?: boolean
          p_event_id: string
          p_exclude_manual?: boolean
          p_exclude_wind_illegal?: boolean
          p_gender: string
          p_indoor?: boolean
          p_limit?: number
          p_offset?: number
          p_only_manual?: boolean
        }
        Returns: {
          athlete_id: string
          athlete_name: string
          birth_date: string
          club_name: string
          date: string
          id: string
          is_national_record: boolean
          meet_id: string
          meet_name: string
          performance: string
          performance_value: number
          result_type: string
          total_count: number
          wind: number
        }[]
      }
      get_duplicate_result_ids: {
        Args: { batch_limit?: number }
        Returns: {
          id: string
        }[]
      }
      gjeldende_klubb_for_utover: {
        Args: { p_athlete_id: string }
        Returns: {
          antall: number
          klubb: string
          sesong: number
        }[]
      }
      is_admin: { Args: never; Returns: boolean }
      is_premium: { Args: { check_user_id: string }; Returns: boolean }
      klubb_sokenokkel: { Args: { p_navn: string }; Returns: string }
      klubb_statistikk: { Args: { p_klubb: string }; Returns: Json }
      klubbrekorder: {
        Args: {
          p_aldersgrupper?: string[]
          p_inne?: boolean
          p_kjonn: string
          p_klubb: string
        }
        Returns: {
          athlete_id: string
          athlete_name: string
          birth_date: string
          date: string
          event_id: string
          meet_city: string
          meet_id: string
          meet_name: string
          performance: string
          performance_value: number
          result_id: string
          result_type: string
          wind: number
        }[]
      }
      parse_performance: {
        Args: {
          perf: string
          res_type: Database["public"]["Enums"]["result_type"]
        }
        Returns: number
      }
      refresh_klubb_bruk_hvis_utdatert: { Args: never; Returns: string }
      refresh_plattform_statistikk: { Args: never; Returns: undefined }
      rett_vindflagg: { Args: { p_event_id: string }; Returns: number }
      rydd_stevnepar: {
        Args: {
          p_behold: string
          p_dry: boolean
          p_fjern: string
          p_flytt: boolean
        }
        Returns: Json
      }
      set_meet_external_ids: { Args: { pairs: Json }; Returns: number }
      sok_klubber: {
        Args: { p_antall?: number; p_sok?: string; p_type?: string }
        Returns: {
          city: string
          club_type: Database["public"]["Enums"]["club_type"]
          id: string
          name: string
          resultater: number
          short_name: string
          totalt: number
          utovere: number
        }[]
      }
      test_innholdsdubletter: {
        Args: { p_event_id: string }
        Returns: {
          antall: number
          athlete_id: string
          created_ats: string[]
          event_id: string
          ids: string[]
          meet_id: string
          performance: string
          place: number
          verifieds: boolean[]
          winds: number[]
        }[]
      }
      test_klubb_fasit: {
        Args: { p_klubb: string }
        Returns: {
          resultater: number
          utovere: number
        }[]
      }
      test_stevnedubletter: {
        Args: { p_fra: string }
        Returns: {
          par: number
          rader: number
        }[]
      }
      test_storste_stevner: {
        Args: { p_antall?: number }
        Returns: {
          id: string
          name: string
          resultater: number
        }[]
      }
      test_storste_utovere: {
        Args: { p_antall?: number }
        Returns: {
          full_name: string
          id: string
          resultater: number
        }[]
      }
      test_utoveravdrift: {
        Args: { p_event_id: string }
        Returns: {
          athlete_ids: string[]
          meet_id: string
          navn: string
          performance: string
          place: number
          result_ids: string[]
        }[]
      }
      test_vindflagg_avvik: {
        Args: never
        Returns: {
          ikke_vindpaavirket_men_flagg: number
          maalt_men_flagg_null: number
          over_2_men_true: number
          umaalt_men_flagg_satt: number
        }[]
      }
      vindflagg: {
        Args: { p_event_id: string; p_wind: number }
        Returns: boolean
      }
    }
    Enums: {
      club_type: "athletics" | "company" | "school" | "foreign" | "other"
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
        | "walking"
        | "other"
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

type DatabaseWithoutInternals = Omit<Database, "__InternalSupabase">

type DefaultSchema = DatabaseWithoutInternals[Extract<keyof Database, "public">]

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends (DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never) = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
      DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
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
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends (DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never) = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
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
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends (DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never) = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
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
    | { schema: keyof DatabaseWithoutInternals },
  EnumName extends (DefaultSchemaEnumNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never) = never,
> = DefaultSchemaEnumNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
    ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
    : never

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    | keyof DefaultSchema["CompositeTypes"]
    | { schema: keyof DatabaseWithoutInternals },
  CompositeTypeName extends (PublicCompositeTypeNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never) = never,
> = PublicCompositeTypeNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof DefaultSchema["CompositeTypes"]
    ? DefaultSchema["CompositeTypes"][PublicCompositeTypeNameOrOptions]
    : never

export const Constants = {
  public: {
    Enums: {
      club_type: ["athletics", "company", "school", "foreign", "other"],
      competition_round: [
        "heat",
        "quarter",
        "semi",
        "final",
        "a_final",
        "b_final",
        "qualification",
      ],
      event_category: [
        "sprint",
        "middle_distance",
        "long_distance",
        "hurdles",
        "steeplechase",
        "relay",
        "jumps",
        "throws",
        "combined",
        "race_walk",
        "walking",
        "other",
      ],
      meet_level: [
        "local",
        "regional",
        "national",
        "championship",
        "international",
      ],
      result_status: ["OK", "DNS", "DNF", "DQ", "NM"],
      result_type: ["time", "distance", "height", "points"],
    },
  },
} as const
