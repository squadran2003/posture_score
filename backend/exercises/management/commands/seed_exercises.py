from django.core.management.base import BaseCommand

from exercises.models import Exercise, ExerciseCategory


CATEGORIES = [
    {"name": "Stretching", "description": "Flexibility and mobility exercises"},
    {"name": "Strengthening", "description": "Muscle strengthening exercises"},
    {"name": "Mobility", "description": "Joint mobility and range of motion"},
    {"name": "Awareness", "description": "Posture awareness and habit-building drills"},
]

EXERCISES = [
    # ── Forward Head (8 exercises) ──────────────────────────
    {
        "name": "Chin Tucks",
        "description": "Retracts the head to align ears over shoulders, counteracting forward head posture.",
        "instructions": "Sit or stand tall. Pull your chin straight back as if making a double chin. Hold for 5 seconds, then relax. Repeat 10 times.",
        "category": "Strengthening",
        "target_issue": "forward_head",
        "difficulty": "beginner",
        "duration_seconds": 60,
        "repetitions": 10,
        "video_url": "https://www.youtube.com/embed/PASTE_ID_HERE",  # Chin Tucks
    },
    {
        "name": "Neck Flexor Stretch",
        "description": "Stretches the tight muscles at the front of the neck that pull the head forward.",
        "instructions": "Tilt your head back gently, looking up at the ceiling. Place one hand on your chest. Hold for 20 seconds. Repeat 3 times.",
        "category": "Stretching",
        "target_issue": "forward_head",
        "difficulty": "beginner",
        "duration_seconds": 90,
        "repetitions": 3,
        "video_url": "https://www.youtube.com/embed/PASTE_ID_HERE",  # Neck Flexor Stretch
    },
    {
        "name": "Suboccipital Release",
        "description": "Relieves tension at the base of the skull caused by forward head posture.",
        "instructions": "Place two tennis balls in a sock. Lie on your back and position them at the base of your skull. Relax and let gravity apply pressure for 2 minutes.",
        "category": "Mobility",
        "target_issue": "forward_head",
        "difficulty": "beginner",
        "duration_seconds": 120,
        "video_url": "https://www.youtube.com/embed/PASTE_ID_HERE",  # Suboccipital Release
    },
    {
        "name": "Deep Neck Flexor Activation",
        "description": "Strengthens the deep neck flexors that support proper head alignment.",
        "instructions": "Lie on your back with knees bent. Tuck your chin slightly and lift your head 1 inch off the floor. Hold for 10 seconds. Repeat 8 times.",
        "category": "Strengthening",
        "target_issue": "forward_head",
        "difficulty": "intermediate",
        "duration_seconds": 120,
        "repetitions": 8,
        "video_url": "https://www.youtube.com/embed/PASTE_ID_HERE",  # Deep Neck Flexor Activation
    },
    {
        "name": "Wall Chin Tucks",
        "description": "A guided version of chin tucks using a wall for feedback.",
        "instructions": "Stand with your back flat against a wall. Pull your chin back trying to touch the wall with the back of your head. Hold 5 seconds. Repeat 10 times.",
        "category": "Strengthening",
        "target_issue": "forward_head",
        "difficulty": "beginner",
        "duration_seconds": 90,
        "repetitions": 10,
        "video_url": "https://www.youtube.com/embed/PASTE_ID_HERE",  # Wall Chin Tucks
    },
    {
        "name": "Cervical Retraction with Band",
        "description": "Uses resistance band to strengthen neck retractors.",
        "instructions": "Loop a resistance band around the back of your head. Hold both ends in front. Push your head back against the band resistance. Hold 5 seconds. Repeat 12 times.",
        "category": "Strengthening",
        "target_issue": "forward_head",
        "difficulty": "intermediate",
        "duration_seconds": 120,
        "repetitions": 12,
        "video_url": "https://www.youtube.com/embed/PASTE_ID_HERE",  # Cervical Retraction with Band
    },
    {
        "name": "Upper Trapezius Stretch",
        "description": "Stretches tight upper traps that contribute to forward head posture.",
        "instructions": "Sit tall. Reach your right hand over your head to your left ear. Gently tilt your head right. Hold 30 seconds. Switch sides.",
        "category": "Stretching",
        "target_issue": "forward_head",
        "difficulty": "beginner",
        "duration_seconds": 90,
        "repetitions": 2,
        "video_url": "https://www.youtube.com/embed/PASTE_ID_HERE",  # Upper Trapezius Stretch
    },
    {
        "name": "Prone Cervical Retraction",
        "description": "Strengthens neck extensors from a face-down position.",
        "instructions": "Lie face down with forehead on a rolled towel. Tuck your chin and lift your head slightly. Hold 5 seconds. Repeat 10 times.",
        "category": "Strengthening",
        "target_issue": "forward_head",
        "difficulty": "intermediate",
        "duration_seconds": 90,
        "repetitions": 10,
        "video_url": "https://www.youtube.com/embed/PASTE_ID_HERE",  # Prone Cervical Retraction
    },
    # ── Shoulder Levelness (6 exercises) ────────────────────
    {
        "name": "Side Neck Stretch",
        "description": "Stretches the lateral neck muscles to help level the shoulders.",
        "instructions": "Sit tall. Drop your right ear toward your right shoulder. Hold for 20 seconds. Repeat on the left side. Do 3 rounds per side.",
        "category": "Stretching",
        "target_issue": "shoulder_level",
        "difficulty": "beginner",
        "duration_seconds": 120,
        "repetitions": 3,
        "video_url": "https://www.youtube.com/embed/PASTE_ID_HERE",  # Side Neck Stretch
    },
    {
        "name": "Lateral Shoulder Raises",
        "description": "Strengthens the deltoids evenly to promote shoulder balance.",
        "instructions": "Stand with a light dumbbell in each hand. Raise both arms out to the sides to shoulder height. Lower slowly. Repeat 12 times for 3 sets.",
        "category": "Strengthening",
        "target_issue": "shoulder_level",
        "difficulty": "intermediate",
        "duration_seconds": 180,
        "repetitions": 12,
        "video_url": "https://www.youtube.com/embed/PASTE_ID_HERE",  # Lateral Shoulder Raises
    },
    {
        "name": "Mirror Shoulder Check",
        "description": "Builds awareness of shoulder asymmetry using visual feedback.",
        "instructions": "Stand in front of a mirror with arms at your sides. Consciously level your shoulders. Hold the corrected position for 30 seconds. Repeat 5 times throughout the day.",
        "category": "Awareness",
        "target_issue": "shoulder_level",
        "difficulty": "beginner",
        "duration_seconds": 30,
        "repetitions": 5,
        "video_url": "https://www.youtube.com/embed/PASTE_ID_HERE",  # Mirror Shoulder Check
    },
    {
        "name": "Unilateral Farmer's Carry",
        "description": "Challenges the core and shoulders to maintain levelness under asymmetric load.",
        "instructions": "Hold a dumbbell or kettlebell in one hand at your side. Walk 30 meters keeping both shoulders level. Switch hands and repeat. 3 rounds per side.",
        "category": "Strengthening",
        "target_issue": "shoulder_level",
        "difficulty": "intermediate",
        "duration_seconds": 180,
        "repetitions": 3,
        "video_url": "https://www.youtube.com/embed/PASTE_ID_HERE",  # Unilateral Farmer's Carry
    },
    {
        "name": "Side-Lying Thoracic Rotation",
        "description": "Improves thoracic spine mobility which affects shoulder position.",
        "instructions": "Lie on your side with knees bent 90 degrees. Extend top arm forward then rotate it open toward the ceiling. Follow with your eyes. Return. Repeat 10 times per side.",
        "category": "Mobility",
        "target_issue": "shoulder_level",
        "difficulty": "beginner",
        "duration_seconds": 120,
        "repetitions": 10,
        "video_url": "https://www.youtube.com/embed/PASTE_ID_HERE",  # Side-Lying Thoracic Rotation
    },
    {
        "name": "Shoulder Shrugs and Drops",
        "description": "Releases tension in the upper trapezius to reset shoulder position.",
        "instructions": "Shrug both shoulders up to your ears. Hold 3 seconds, then let them drop completely. Repeat 10 times. Focus on the release.",
        "category": "Mobility",
        "target_issue": "shoulder_level",
        "difficulty": "beginner",
        "duration_seconds": 60,
        "repetitions": 10,
        "video_url": "https://www.youtube.com/embed/PASTE_ID_HERE",  # Shoulder Shrugs and Drops
    },
    # ── Shoulder Rounding (8 exercises) ─────────────────────
    {
        "name": "Doorway Pec Stretch",
        "description": "Opens the chest to counteract rounded shoulders.",
        "instructions": "Stand in a doorway with arms at 90 degrees on the frame. Step one foot forward until you feel a stretch across your chest. Hold 30 seconds. Repeat 3 times.",
        "category": "Stretching",
        "target_issue": "shoulder_round",
        "difficulty": "beginner",
        "duration_seconds": 120,
        "repetitions": 3,
        "video_url": "https://www.youtube.com/embed/PASTE_ID_HERE",  # Doorway Pec Stretch
    },
    {
        "name": "Band Pull-Aparts",
        "description": "Strengthens the rear deltoids and rhomboids to pull shoulders back.",
        "instructions": "Hold a resistance band with both hands at shoulder width, arms straight in front. Pull the band apart by squeezing your shoulder blades. Return slowly. Repeat 15 times.",
        "category": "Strengthening",
        "target_issue": "shoulder_round",
        "difficulty": "beginner",
        "duration_seconds": 90,
        "repetitions": 15,
        "video_url": "https://www.youtube.com/embed/PASTE_ID_HERE",  # Band Pull-Aparts
    },
    {
        "name": "Prone Y-T-W Raises",
        "description": "Activates the lower trapezius and rhomboids from a face-down position.",
        "instructions": "Lie face down on a bench or floor. Raise arms into a Y shape, hold 5 seconds. Then T shape, hold 5 seconds. Then W shape, hold 5 seconds. Repeat 8 rounds.",
        "category": "Strengthening",
        "target_issue": "shoulder_round",
        "difficulty": "intermediate",
        "duration_seconds": 180,
        "repetitions": 8,
        "video_url": "https://www.youtube.com/embed/PASTE_ID_HERE",  # Prone Y-T-W Raises
    },
    {
        "name": "Wall Angels",
        "description": "Improves shoulder mobility and scapular control against a wall.",
        "instructions": "Stand with your back, head, and arms against a wall. Slowly slide arms up and down like making a snow angel. Keep everything touching the wall. Repeat 10 times.",
        "category": "Mobility",
        "target_issue": "shoulder_round",
        "difficulty": "beginner",
        "duration_seconds": 120,
        "repetitions": 10,
        "video_url": "https://www.youtube.com/embed/PASTE_ID_HERE",  # Wall Angels
    },
    {
        "name": "Seated Row",
        "description": "Strengthens the mid-back muscles that retract the shoulder blades.",
        "instructions": "Sit with a resistance band looped around your feet. Pull the band toward your waist, squeezing shoulder blades together. Return slowly. 3 sets of 12.",
        "category": "Strengthening",
        "target_issue": "shoulder_round",
        "difficulty": "intermediate",
        "duration_seconds": 180,
        "repetitions": 12,
        "video_url": "https://www.youtube.com/embed/PASTE_ID_HERE",  # Seated Row
    },
    {
        "name": "Thoracic Extension Over Roller",
        "description": "Mobilizes the thoracic spine to open the chest.",
        "instructions": "Place a foam roller under your upper back. Support your head with your hands. Gently extend back over the roller. Hold 5 seconds at each segment. Work up and down for 2 minutes.",
        "category": "Mobility",
        "target_issue": "shoulder_round",
        "difficulty": "beginner",
        "duration_seconds": 120,
        "video_url": "https://www.youtube.com/embed/PASTE_ID_HERE",  # Thoracic Extension Over Roller
    },
    {
        "name": "Face Pulls",
        "description": "Targets the rear deltoids and external rotators to correct rounded shoulders.",
        "instructions": "Using a cable or band at face height, pull toward your face with elbows high. Squeeze shoulder blades at the end. Return slowly. 3 sets of 15.",
        "category": "Strengthening",
        "target_issue": "shoulder_round",
        "difficulty": "intermediate",
        "duration_seconds": 180,
        "repetitions": 15,
        "video_url": "https://www.youtube.com/embed/PASTE_ID_HERE",  # Face Pulls
    },
    {
        "name": "Chest Opener Stretch",
        "description": "A simple standing stretch to open the front of the shoulders.",
        "instructions": "Clasp your hands behind your back. Straighten your arms and lift them gently while squeezing your shoulder blades together. Hold 20 seconds. Repeat 3 times.",
        "category": "Stretching",
        "target_issue": "shoulder_round",
        "difficulty": "beginner",
        "duration_seconds": 90,
        "repetitions": 3,
        "video_url": "https://www.youtube.com/embed/PASTE_ID_HERE",  # Chest Opener Stretch
    },
    # ── Spine Alignment (8 exercises) ───────────────────────
    {
        "name": "Cat-Cow Stretch",
        "description": "Mobilizes the entire spine through flexion and extension.",
        "instructions": "Start on hands and knees. Arch your back toward the ceiling (cat), then drop your belly toward the floor (cow). Alternate slowly for 10 reps.",
        "category": "Mobility",
        "target_issue": "spine_align",
        "difficulty": "beginner",
        "duration_seconds": 90,
        "repetitions": 10,
        "video_url": "https://www.youtube.com/embed/PASTE_ID_HERE",  # Cat-Cow Stretch
    },
    {
        "name": "Bird-Dog",
        "description": "Strengthens the core stabilizers that keep the spine aligned.",
        "instructions": "Start on hands and knees. Extend your right arm forward and left leg back simultaneously. Hold 5 seconds. Switch sides. Repeat 10 times per side.",
        "category": "Strengthening",
        "target_issue": "spine_align",
        "difficulty": "beginner",
        "duration_seconds": 120,
        "repetitions": 10,
        "video_url": "https://www.youtube.com/embed/PASTE_ID_HERE",  # Bird-Dog
    },
    {
        "name": "Dead Bug",
        "description": "Trains core stability while maintaining a neutral spine.",
        "instructions": "Lie on your back with arms reaching toward the ceiling, knees bent 90 degrees. Lower opposite arm and leg toward the floor. Return and switch. 10 reps per side.",
        "category": "Strengthening",
        "target_issue": "spine_align",
        "difficulty": "beginner",
        "duration_seconds": 120,
        "repetitions": 10,
        "video_url": "https://www.youtube.com/embed/PASTE_ID_HERE",  # Dead Bug
    },
    {
        "name": "Plank",
        "description": "Builds endurance in the core muscles that support spinal alignment.",
        "instructions": "Hold a forearm plank position with body in a straight line from head to heels. Keep your core tight and hips level. Hold for 30-60 seconds. Repeat 3 times.",
        "category": "Strengthening",
        "target_issue": "spine_align",
        "difficulty": "intermediate",
        "duration_seconds": 180,
        "repetitions": 3,
        "video_url": "https://www.youtube.com/embed/PASTE_ID_HERE",  # Plank
    },
    {
        "name": "Side Plank",
        "description": "Strengthens the lateral core muscles to prevent side-leaning.",
        "instructions": "Lie on your side. Prop yourself up on your forearm. Lift your hips to form a straight line. Hold 20-30 seconds. Switch sides. 3 rounds per side.",
        "category": "Strengthening",
        "target_issue": "spine_align",
        "difficulty": "intermediate",
        "duration_seconds": 180,
        "repetitions": 3,
        "video_url": "https://www.youtube.com/embed/PASTE_ID_HERE",  # Side Plank
    },
    {
        "name": "Seated Spinal Twist",
        "description": "Improves rotational mobility of the spine.",
        "instructions": "Sit on the floor with legs extended. Bend your right knee and cross it over your left leg. Twist your torso to the right. Hold 20 seconds. Switch sides.",
        "category": "Stretching",
        "target_issue": "spine_align",
        "difficulty": "beginner",
        "duration_seconds": 60,
        "repetitions": 2,
        "video_url": "https://www.youtube.com/embed/PASTE_ID_HERE",  # Seated Spinal Twist
    },
    {
        "name": "Pallof Press",
        "description": "Anti-rotation exercise that trains the core to resist lateral forces.",
        "instructions": "Stand sideways to a cable or band. Hold the handle at your chest. Press straight out, resisting the pull. Hold 3 seconds. Return. 10 reps per side.",
        "category": "Strengthening",
        "target_issue": "spine_align",
        "difficulty": "intermediate",
        "duration_seconds": 120,
        "repetitions": 10,
        "video_url": "https://www.youtube.com/embed/PASTE_ID_HERE",  # Pallof Press
    },
    {
        "name": "Wall Sit with Alignment",
        "description": "Builds endurance in the legs and core while practicing spinal alignment.",
        "instructions": "Slide your back down a wall until thighs are parallel to the floor. Press your lower back flat against the wall. Hold for 30 seconds. Repeat 3 times.",
        "category": "Strengthening",
        "target_issue": "spine_align",
        "difficulty": "beginner",
        "duration_seconds": 120,
        "repetitions": 3,
        "video_url": "https://www.youtube.com/embed/PASTE_ID_HERE",  # Wall Sit with Alignment
    },
    # ── General Posture (6 exercises) ───────────────────────
    {
        "name": "Posture Reset Drill",
        "description": "A quick full-body posture reset you can do anytime.",
        "instructions": "Stand tall. Roll shoulders back and down. Tuck chin slightly. Engage core. Squeeze glutes gently. Hold for 10 seconds. Repeat 5 times throughout the day.",
        "category": "Awareness",
        "target_issue": "general",
        "difficulty": "beginner",
        "duration_seconds": 60,
        "repetitions": 5,
        "video_url": "https://www.youtube.com/embed/PASTE_ID_HERE",  # Posture Reset Drill
    },
    {
        "name": "Brugger's Relief Position",
        "description": "Counteracts the sitting posture by opening the chest and activating the back.",
        "instructions": "Sit at the edge of your chair. Spread knees apart, turn palms forward, squeeze shoulder blades together, tuck chin. Hold 10 seconds. Do every 30 minutes while sitting.",
        "category": "Awareness",
        "target_issue": "general",
        "difficulty": "beginner",
        "duration_seconds": 30,
        "repetitions": 10,
        "video_url": "https://www.youtube.com/embed/PASTE_ID_HERE",  # Brugger's Relief Position
    },
    {
        "name": "Full Body Stretch Routine",
        "description": "A 5-minute stretching routine targeting all major posture muscles.",
        "instructions": "Perform each for 30 seconds: neck side stretch (each side), chest opener, cat-cow, standing hamstring stretch, hip flexor stretch. Complete 1 full round.",
        "category": "Stretching",
        "target_issue": "general",
        "difficulty": "beginner",
        "duration_seconds": 300,
        "video_url": "https://www.youtube.com/embed/PASTE_ID_HERE",  # Full Body Stretch Routine
    },
    {
        "name": "Glute Bridge",
        "description": "Strengthens the glutes and hamstrings that support pelvic alignment.",
        "instructions": "Lie on your back with knees bent, feet flat. Push through your heels to lift your hips. Squeeze glutes at the top. Hold 3 seconds. Lower. Repeat 15 times.",
        "category": "Strengthening",
        "target_issue": "general",
        "difficulty": "beginner",
        "duration_seconds": 120,
        "repetitions": 15,
        "video_url": "https://www.youtube.com/embed/PASTE_ID_HERE",  # Glute Bridge
    },
    {
        "name": "Hip Flexor Stretch",
        "description": "Lengthens tight hip flexors that contribute to anterior pelvic tilt.",
        "instructions": "Kneel on one knee in a lunge position. Push your hips forward until you feel a stretch in the front of your back hip. Hold 30 seconds. Switch sides. 3 rounds.",
        "category": "Stretching",
        "target_issue": "general",
        "difficulty": "beginner",
        "duration_seconds": 180,
        "repetitions": 3,
        "video_url": "https://www.youtube.com/embed/PASTE_ID_HERE",  # Hip Flexor Stretch
    },
    {
        "name": "Posture Timer Challenge",
        "description": "Build posture endurance by holding correct posture for increasing durations.",
        "instructions": "Set a timer. Sit or stand with perfect posture. When you notice yourself slouching, note the time. Try to beat your record each day. Start with 5-minute intervals.",
        "category": "Awareness",
        "target_issue": "general",
        "difficulty": "beginner",
        "duration_seconds": 300,
        "video_url": "https://www.youtube.com/embed/PASTE_ID_HERE",  # Posture Timer Challenge
    },
]


class Command(BaseCommand):
    help = "Seed the exercise database with initial exercises"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete all existing exercises before seeding",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            Exercise.objects.all().delete()
            ExerciseCategory.objects.all().delete()
            self.stdout.write(self.style.WARNING("Cleared existing exercises and categories."))

        # Create categories
        cat_map = {}
        for cat_data in CATEGORIES:
            cat, created = ExerciseCategory.objects.get_or_create(
                name=cat_data["name"],
                defaults={"description": cat_data["description"]},
            )
            cat_map[cat.name] = cat
            if created:
                self.stdout.write(f"  Created category: {cat.name}")

        # Create exercises
        created_count = 0
        skipped_count = 0
        for ex_data in EXERCISES:
            ex_data = ex_data.copy()
            category = cat_map[ex_data.pop("category")]
            # Skip placeholder video URLs
            video_url = ex_data.get("video_url", "")
            if "PASTE_ID_HERE" in video_url:
                ex_data["video_url"] = ""
            _, created = Exercise.objects.get_or_create(
                name=ex_data["name"],
                defaults={**ex_data, "category": category},
            )
            if created:
                created_count += 1
            else:
                skipped_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done! Created {created_count} exercises, skipped {skipped_count} (already exist)."
            )
        )
