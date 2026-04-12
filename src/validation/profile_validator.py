"""Input validation for user profiles."""

from typing import List, Tuple


class ProfileValidator:
    """Validates user profile inputs"""
    
    @staticmethod
    def validate_age(age: int) -> Tuple[bool, str]:
        """Validate age is between 18 and 80"""
        if not 18 <= age <= 80:
            return False, "Age must be between 18 and 80"
        return True, ""
    
    @staticmethod
    def validate_experience(experience: int, age: int) -> Tuple[bool, str]:
        """Validate experience is reasonable for age"""
        max_exp = age - 16  # Assume work starts at 16 earliest
        if experience > max_exp:
            return False, f"Experience ({experience} years) exceeds reasonable maximum for age {age}"
        if experience < 0:
            return False, "Experience cannot be negative"
        return True, ""
    
    @staticmethod
    def validate_performance_rating(rating: int) -> Tuple[bool, str]:
        """Validate performance rating is 1-5"""
        if not 1 <= rating <= 5:
            return False, "Performance rating must be between 1 and 5"
        return True, ""
    
    @staticmethod
    def validate_required_fields(skills: List[str], industry: str, role_level: str) -> Tuple[bool, List[str]]:
        """Check all required fields are present"""
        errors = []
        if not skills:
            errors.append("Skills are required")
        if not industry:
            errors.append("Industry is required")
        if not role_level:
            errors.append("Role level is required")
        return len(errors) == 0, errors
