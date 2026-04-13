"""Career path visualization components."""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict
import pandas as pd

from src.analytics.career_path_modeler import CareerPath, CareerTransition


class CareerPathVisualizer:
    """Creates interactive career path visualizations"""
    
    def render_path_overview(self, paths: List[CareerPath]) -> None:
        """Render overview of all career paths"""
        
        if not paths:
            st.info("No career paths available. Try adjusting your profile.")
            return
        
        st.markdown("#### 🎯 Career Path Options")
        
        # Create comparison table
        path_data = []
        for i, path in enumerate(paths):
            path_data.append({
                "Path": path.path_name,
                "Success %": f"{path.overall_success_probability:.0f}%",
                "Timeline": path.total_timeline,
                "Salary Growth": path.total_salary_growth,
                "Market Viability": path.market_viability.title(),
                "Key Skills Needed": len(path.transitions[0].skill_gaps) if path.transitions else 0
            })
        
        df = pd.DataFrame(path_data)
        
        # Style the dataframe
        styled_df = df.style.format({
            "Success %": "{}",
            "Key Skills Needed": "{} skills"
        })
        
        st.dataframe(styled_df, use_container_width=True)
    
    def render_detailed_path(self, path: CareerPath) -> None:
        """Render detailed view of a single career path"""
        
        st.markdown(f"### 🚀 {path.path_name}")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Success Probability", f"{path.overall_success_probability:.0f}%")
        
        with col2:
            st.metric("Timeline", path.total_timeline)
        
        with col3:
            st.metric("Salary Growth", path.total_salary_growth)
        
        with col4:
            viability_colors = {
                "excellent": "🟢",
                "good": "🟡", 
                "fair": "🟠",
                "limited": "🔴"
            }
            icon = viability_colors.get(path.market_viability, "⚪")
            st.metric("Market Viability", f"{icon} {path.market_viability.title()}")
        
        # Transition details
        if path.transitions:
            transition = path.transitions[0]  # For now, show first transition
            
            st.markdown("---")
            st.markdown("#### 📊 Market Analysis")
            
            # Market insights
            if transition.market_insights:
                for insight in transition.market_insights:
                    st.markdown(f"- {insight}")
            
            # Skills analysis
            st.markdown("#### 🎯 Skills Analysis")
            
            col_skills1, col_skills2 = st.columns(2)
            
            with col_skills1:
                st.markdown("**Required Skills:**")
                for skill in transition.required_skills:
                    st.markdown(f"✅ {skill.title()}")
            
            with col_skills2:
                if transition.skill_gaps:
                    st.markdown("**Skills to Learn:**")
                    for skill in transition.skill_gaps:
                        st.markdown(f"📚 {skill.title()}")
                else:
                    st.markdown("**✅ All required skills present!**")
            
            # Success factors visualization
            self._render_success_factors(transition)
    
    def _render_success_factors(self, transition: CareerTransition) -> None:
        """Render success factors breakdown"""
        
        st.markdown("#### 📈 Success Factors")
        
        # Create a simple success factor visualization
        factors = {
            "Market Demand": self._get_demand_score(transition.market_demand),
            "Skill Match": max(20, 100 - len(transition.skill_gaps) * 15),
            "Timeline": 80 if "months" in transition.time_to_transition else 60,
            "Industry Growth": 75  # Simplified
        }
        
        # Create horizontal bar chart
        fig = go.Figure()
        
        colors = ['#10b981', '#f59e0b', '#ef4444', '#6366f1']
        
        for i, (factor, score) in enumerate(factors.items()):
            fig.add_trace(go.Bar(
                y=[factor],
                x=[score],
                orientation='h',
                marker_color=colors[i % len(colors)],
                text=f"{score}%",
                textposition='inside',
                name=factor
            ))
        
        fig.update_layout(
            title="Success Factor Analysis",
            xaxis_title="Score (%)",
            xaxis=dict(range=[0, 100]),
            height=300,
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_action_plan(self, path: CareerPath) -> None:
        """Render actionable plan for the career path"""
        
        st.markdown("#### 📋 Action Plan")
        
        # Milestones
        if path.key_milestones:
            st.markdown("**Key Milestones:**")
            for i, milestone in enumerate(path.key_milestones, 1):
                st.markdown(f"{i}. {milestone}")
        
        # Recommendations
        if path.recommended_actions:
            st.markdown("**Recommended Actions:**")
            for action in path.recommended_actions:
                st.markdown(f"• {action}")
        
        # Timeline visualization
        if path.transitions:
            self._render_timeline(path.transitions[0])
    
    def _render_timeline(self, transition: CareerTransition) -> None:
        """Render timeline for skill development"""
        
        if not transition.skill_gaps:
            st.success("✅ No additional skills needed!")
            return
        
        st.markdown("**Learning Timeline:**")
        
        # Estimate learning time for each skill
        skill_times = {}
        for skill in transition.skill_gaps:
            if "leadership" in skill.lower() or "management" in skill.lower():
                skill_times[skill] = "3-6 months"
            elif "technical" in skill.lower() or "system" in skill.lower():
                skill_times[skill] = "2-4 months"
            else:
                skill_times[skill] = "1-3 months"
        
        # Display as timeline
        for skill, time in skill_times.items():
            st.markdown(f"📚 **{skill.title()}** - {time}")
    
    def render_salary_projection(self, path: CareerPath) -> None:
        """Render salary growth projection"""
        
        st.markdown("#### 💰 Salary Projection")
        
        if path.transitions:
            transition = path.transitions[0]
            
            # Simple salary projection visualization
            current_salary = 100  # Normalized to 100%
            
            # Extract percentage from salary_change string
            if "+" in transition.salary_change:
                try:
                    pct_str = transition.salary_change.replace("+", "").replace("%", "").split("-")[0]
                    growth_pct = float(pct_str)
                    future_salary = current_salary + growth_pct
                except:
                    future_salary = current_salary + 25  # Default 25% growth
            else:
                future_salary = current_salary
            
            # Create simple bar chart
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=["Current Role", "Target Role"],
                y=[current_salary, future_salary],
                marker_color=['#6366f1', '#10b981'],
                text=[f"{current_salary}%", f"{future_salary}%"],
                textposition='inside'
            ))
            
            fig.update_layout(
                title="Salary Growth Projection",
                yaxis_title="Relative Salary (%)",
                height=300,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white')
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.caption(f"Expected salary change: {transition.salary_change}")
    
    def render_market_comparison(self, paths: List[CareerPath]) -> None:
        """Render market comparison of different paths"""
        
        if len(paths) < 2:
            return
        
        st.markdown("#### 📊 Market Comparison")
        
        # Create radar chart comparing paths
        categories = ['Success Probability', 'Market Demand', 'Salary Growth', 'Timeline Score']
        
        fig = go.Figure()
        
        colors = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
        
        for i, path in enumerate(paths[:3]):  # Show top 3 paths
            if path.transitions:
                transition = path.transitions[0]
                
                # Calculate scores
                timeline_score = 100 if "months" in transition.time_to_transition else 70
                demand_score = self._get_demand_score(transition.market_demand)
                salary_score = self._extract_salary_score(transition.salary_change)
                
                values = [
                    path.overall_success_probability,
                    demand_score,
                    salary_score,
                    timeline_score
                ]
                
                fig.add_trace(go.Scatterpolar(
                    r=values,
                    theta=categories,
                    fill='toself',
                    name=path.path_name,
                    line_color=colors[i % len(colors)]
                ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            showlegend=True,
            height=400,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _get_demand_score(self, demand_level: str) -> float:
        """Convert demand level to numeric score"""
        
        demand_scores = {
            "very_high": 95,
            "high": 85,
            "medium": 70,
            "low": 50,
            "very_low": 30
        }
        
        return demand_scores.get(demand_level, 70)
    
    def _extract_salary_score(self, salary_change: str) -> float:
        """Extract salary score from salary change string"""
        
        if "+" in salary_change:
            try:
                pct_str = salary_change.replace("+", "").replace("%", "").split("-")[0]
                return min(100, float(pct_str) * 2)  # Scale to 0-100
            except:
                return 70
        else:
            return 50  # No change
    
    def render_path_selector(self, paths: List[CareerPath]) -> int:
        """Render path selector and return selected index"""
        
        if not paths:
            return 0
        
        path_options = []
        for i, path in enumerate(paths):
            success_icon = "🟢" if path.overall_success_probability >= 70 else "🟡" if path.overall_success_probability >= 50 else "🔴"
            path_options.append(f"{success_icon} {path.path_name} ({path.overall_success_probability:.0f}% success)")
        
        selected = st.selectbox(
            "Choose a career path to explore:",
            options=range(len(path_options)),
            format_func=lambda x: path_options[x],
            help="Paths are ranked by success probability and market viability"
        )
        
        return selected