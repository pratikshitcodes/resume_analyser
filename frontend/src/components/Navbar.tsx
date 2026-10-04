import React from 'react';
import { useAuth } from '../context/AuthContext';
import { Sparkles, UserCheck, Briefcase, LogOut, UserCircle } from 'lucide-react';

interface NavbarProps {
  onOpenAuth: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onOpenAuth }) => {
  const { user, role, switchRole, logout } = useAuth();

  return (
    <header className="sticky top-0 z-50 backdrop-blur-md bg-slate-900/90 border-b border-slate-800/90 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Brand Logo & Zoho Zia Micro-Accent */}
        <div className="flex items-center space-x-3">
          {/* Zoho 4-color micro brand accent */}
          <div className="hidden sm:flex flex-col space-y-0.5 justify-center p-1 rounded bg-slate-950/60 border border-slate-800">
            <div className="flex space-x-0.5">
              <span className="w-1.5 h-1.5 rounded-sm bg-[#EA4335]"></span>
              <span className="w-1.5 h-1.5 rounded-sm bg-[#0F9D58]"></span>
            </div>
            <div className="flex space-x-0.5">
              <span className="w-1.5 h-1.5 rounded-sm bg-[#1A73E8]"></span>
              <span className="w-1.5 h-1.5 rounded-sm bg-[#FBBC04]"></span>
            </div>
          </div>

          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-purple-600 flex items-center justify-center shadow-md shadow-indigo-500/25">
            <Sparkles className="w-4 h-4 text-white" />
          </div>

          <div>
            <div className="flex items-center space-x-2">
              <span className="text-base sm:text-lg font-bold bg-gradient-to-r from-white via-slate-100 to-indigo-200 bg-clip-text text-transparent tracking-tight">
                TalentPulse AI
              </span>
              <span className="hidden sm:inline-flex items-center space-x-1 text-[11px] px-2 py-0.5 rounded-full bg-indigo-950/80 text-indigo-300 border border-indigo-800/60 font-medium">
                <Sparkles className="w-2.5 h-2.5 text-indigo-400" />
                <span>Zia Engine</span>
              </span>
            </div>
            <p className="text-[10px] text-slate-400 hidden md:block">AI ATS & Intelligent Recruitment Suite</p>
          </div>
        </div>

        {/* Mode Switcher */}
        <div className="flex items-center bg-slate-950/80 p-1 rounded-xl border border-slate-800 shadow-inner">
          <button
            onClick={() => switchRole('candidate')}
            className={`flex items-center space-x-2 px-3 sm:px-4 py-1.5 rounded-lg text-xs sm:text-sm font-semibold transition-all duration-200 ${
              role === 'candidate'
                ? 'bg-gradient-to-r from-indigo-600 to-violet-600 text-white shadow-md shadow-indigo-500/25'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
            }`}
          >
            <UserCheck className="w-4 h-4 text-indigo-400" />
            <span>Candidate Studio</span>
          </button>

          <button
            onClick={() => switchRole('recruiter')}
            className={`flex items-center space-x-2 px-3 sm:px-4 py-1.5 rounded-lg text-xs sm:text-sm font-semibold transition-all duration-200 ${
              role === 'recruiter'
                ? 'bg-gradient-to-r from-emerald-600 to-teal-600 text-white shadow-md shadow-emerald-500/25'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
            }`}
          >
            <Briefcase className="w-4 h-4 text-emerald-400" />
            <span>Recruiter Matrix</span>
          </button>
        </div>

        {/* User Status / Login */}
        <div className="flex items-center space-x-3">
          {user ? (
            <div className="flex items-center space-x-3">
              <div className="hidden md:flex flex-col text-right">
                <span className="text-xs font-semibold text-slate-200">{user.full_name || user.email}</span>
                <span className="text-[10px] text-emerald-400 capitalize flex items-center justify-end space-x-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 inline-block animate-pulse"></span>
                  <span>{role} • active</span>
                </span>
              </div>
              <button
                onClick={logout}
                title="Logout"
                className="p-2 rounded-xl bg-slate-800/80 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors border border-slate-700/60"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <button
              onClick={onOpenAuth}
              className="flex items-center space-x-2 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold transition-colors shadow-sm shadow-indigo-600/30"
            >
              <UserCircle className="w-4 h-4" />
              <span>Sign In</span>
            </button>
          )}
        </div>

      </div>
    </header>
  );
};
