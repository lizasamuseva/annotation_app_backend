from rest_framework import serializers


class FiltersSerializer(serializers.Serializer):
    Neuro = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text='Example: ["Arousal"]'
    )
    SpO2 = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text='Example: ["RelativeDesaturation"]'
    )
    Respiratory = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text='Example: ["ObstructiveApnea", "MixedApnea", "Hypopnea", "CentralApnea"]'
    )
    Nasal = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text='Example: ["Snore"]'
    )
    Cardiac = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text='Example: ["Tachycardia", "Bradycardia"]'
    )
    SleepStages = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text='Example: ["NonREM1", "NonREM2", "Wake"]'
    )
    BodyPositions = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text='Example: ["Left", "Supine", "Prone", "Right", "Up"]'
    )


class FiltersResultWrapperSerializer(serializers.Serializer):
    filters = FiltersSerializer()


class FiltersResponseSerializer(serializers.Serializer):
    result = FiltersResultWrapperSerializer()
