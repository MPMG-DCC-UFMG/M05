from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

class Config(models.Model):
    ALGORITHMS = (
        ('BM25', 'Okapi BM25'),
        ('DFR', 'Divergence from Randomness (DFR)'),
        ('DFI', 'Divergence from Independence (DFI)'),
        ('IB', 'Information based model'),
        ('LMDirichlet', 'Language Model: Dirichlet priors'),
        ('LMJelinekMercer', 'Language Model: Jelinek-Mercer smoothing method'),
    )

    NORMALIZATIONS = (
        ('no', 'no'),
        ('h1', 'h1'),
        ('h2', 'h2'),
        ('h3', 'h3'),
        ('z', 'z'),
    )

    BASIC_MODELS = (
        ('g', 'Geometric approximation of Bose-Einstein'),
        ('if', 'Inverse Term Frequency'),
        ('in', 'Inverse Document Frequency'),
        ('ine', 'Inverse Expected Document Frequency'),
    )

    AFTER_EFFECTS = (
        ('b', 'Bernoulli processes'),
        ('l', "Laplace's law of succession"),
    )

    IND_MEASURES = (
        ('standardized', 'Standardized'),
        ('saturated', 'Saturated'),
        ('chisquared', 'Normalized chi-squared'),
    )

    DISTRIBUTIONS = (
        ('ll', 'Log-logistic'),
        ('spl', 'Smoothed power-law'),
    )

    LAMBDAS = (
        ('df', 'Document frequency'),
        ('ttf', 'Total term frequency'),
    )

    INDICES = (
        ('regular', 'Regular'),
        ('replica', 'Replicas'),
    )

    # compare = models.CharField(max_length=10, choices=INDICES, default='')
    algorithm = models.CharField(
        max_length=50, choices=ALGORITHMS, blank=False, default='BM25')
    num_repl = models.PositiveSmallIntegerField(
        default=1, validators=[MaxValueValidator(50), MinValueValidator(0)])
    max_result_window = models.PositiveIntegerField(
        default=10000, validators=[MinValueValidator(1)])
    # BM25 parameters
    k1 = models.CharField(max_length=10, default='1.2')
    b = models.CharField(max_length=10, default='0.75')
    discount_overlaps = models.CharField(
        max_length=10, default='True', choices=(('true', 'True'), ('false', 'False')))
    # DFR parameters
    basic_model = models.CharField(
        max_length=10, choices=BASIC_MODELS, blank=False, default='g')
    after_effect = models.CharField(
        max_length=10, choices=AFTER_EFFECTS, blank=False, default='b')
    normalization_dfr = models.CharField(
        max_length=10, choices=NORMALIZATIONS, blank=False, default='h1')
    normalization_parameter_dfr = models.CharField(
        max_length=10, default='1.0')

    # DFI parameters
    independence_measure = models.CharField(
        max_length=15, choices=IND_MEASURES, blank=False, default='standardized')

    # IB parameters
    distribution = models.CharField(
        max_length=10, choices=DISTRIBUTIONS, blank=False, default='ll')
    lambda_ib = models.CharField(
        max_length=10, choices=LAMBDAS, blank=False, default='df')
    normalization_ib = models.CharField(
        max_length=10, choices=NORMALIZATIONS, blank=False, default='h1')
    normalization_parameter_ib = models.CharField(max_length=10, default='1.0')

    # LM Dirichlet parameters
    mu = models.CharField(max_length=10, default='2000')

    # LM Jelinek Mercer parameters
    lambda_jelinek = models.CharField(max_length=10, default='.1')
